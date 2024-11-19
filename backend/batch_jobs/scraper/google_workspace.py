import asyncio
import re
import urllib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import quote

import aiohttp
import requests
from bs4 import BeautifulSoup
from peewee import fn
from pydantic import BaseModel
from supawee.client import connect_to_postgres

from batch_jobs.common import (
    ASYNC_IO_MAX_PARALLELISM,
    find_tag_and_get_text,
    listing_updated_str_to_date,
    extract_number_best_effort,
    is_html_in_english,
    standardize_url,
)
from batch_jobs.scraper.search_terms import GOOGLE_WORKSPACE_SEARCH_TERMS
from batch_jobs.scraper.settings import should_save_large_fields
from common.company import standardize_company_name
from common.config import POSTGRES_DATABASE_URL
from supabase.models.data import GoogleWorkspace

# TODO: crawling /marketplace/search/ is against robots.txt :/
SEARCH_URL = "https://workspace.google.com/marketplace/search/"
# but maybe if i show some respect / restraint in say crawling only every week
# and only listings directly from the marketplace, it might be okay
# https://chatgpt.com/share/672ac15b-46d8-8005-8534-8de9c2f4c616
# I wonder how Semrush, SimilarWeb, etc. do it? No idea how they can have agreements with all websites.

# TODO(P00, compliance): We need to bring the crawler up-to-date to Data standards
# Web Scraping Policies
# 1. Data
# Do you provide data in raw form? If not, do you anonymize, aggregate or summarize the data before providing it?
# (b) Has any PII contained in the data been removed, anonymized, or aggregated such that it cannot be used to identify an individual?
#  => Even publicly available contact data is considered PII
# 2. Terms of Service and Methodologies
# (a) When scraping a site, do you agree to Terms of Service (TOS), including but not limited to, automated “click throughs”? This often occurs when creating an account.
#   => You implicitly agree to the TOS when you use the website
#    THEIR TOS 3.3.
#    3.3 For example, you must not access (or attempt to access) the Market through any automated means
#    (including use of scripts, crawlers, or similar technologies)
#    and you must ensure that you comply with the instructions set out in any robots.txt file
#    present on the Market website.
# (b) Do you resolve captchas?
#    => No
#
# 3. Do you create an account to gain access to information?
#    => No

# 4. If you engage in any behavior to mask your identity / IP addresses,
#    => No, BUT TODO(P00, compliance): Include a User-Agent header in the request
#
# (a) Is it traceable back to your company?
#
# (b) Is there a way for your company to be contacted?
#
# (c) Is your company name included in the metadata of each request?
#
#
# 5. Do you take steps not to interfere with a site’s functionality? If yes, what are they?

LISTS = [SEARCH_URL + quote(term) for term in GOOGLE_WORKSPACE_SEARCH_TERMS] + [
    # MAIN categories
    "https://workspace.google.com/marketplace",
    "https://workspace.google.com/marketplace/category/intelligent-apps",
    "https://workspace.google.com/marketplace/category/work-from-everywhere",
    "https://workspace.google.com/marketplace/category/business-essentials",
    "https://workspace.google.com/marketplace/category/apps-to-discover",
    "https://workspace.google.com/marketplace/category/google-apps",
    "https://workspace.google.com/marketplace/category/popular-apps",
    "https://workspace.google.com/marketplace/category/top-rated",
    "https://workspace.google.com/marketplace/category/business-tools/accounting-and-finance",
    "https://workspace.google.com/marketplace/category/business-tools/administration-and-management",
    "https://workspace.google.com/marketplace/category/business-tools/erp-and-logistics",
    "https://workspace.google.com/marketplace/category/business-tools/hr-and-legal",
    "https://workspace.google.com/marketplace/category/business-tools/marketing-and-analytics",
    "https://workspace.google.com/marketplace/category/business-tools/sales-and-crm",
    "https://workspace.google.com/marketplace/category/productivity/creative-tools",
    "https://workspace.google.com/marketplace/category/productivity/web-development",
    "https://workspace.google.com/marketplace/category/productivity/office-applications",
    "https://workspace.google.com/marketplace/category/productivity/task-management",
    "https://workspace.google.com/marketplace/category/education/academic-resources",
    "https://workspace.google.com/marketplace/category/education/teacher-and-admin-tools",
    "https://workspace.google.com/marketplace/category/communication",
    "https://workspace.google.com/marketplace/category/utilities",
]


class ScrapeAddOnDetailsJob(BaseModel):
    # can either be a marketplace_link OR wayback url
    url: str
    # Y-m-d, also determines the format of the data to be scraped
    p_date: str

    # plugin identification
    name: Optional[str] = None
    google_id: Optional[str] = None
    marketplace_link: Optional[str] = None


def get_google_id_from_marketplace_link(link: str):
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


def get_add_ons_from_listing_page(
    listing_url: str, p_date: str
) -> List[ScrapeAddOnDetailsJob]:
    print(f"getting add_ons from marketplace listing page {listing_url}")
    # Send a request to the URL
    response = requests.get(listing_url)
    if response.status_code != 200:
        print(f"WARNING: cannot fetch data from url {listing_url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    add_on_elements = soup.find_all("a", class_="RwHvCd")
    result = []
    for add_on_element in add_on_elements:
        name = find_tag_and_get_text(add_on_element, "div", "M0atNd")
        # [1:] removes the first dot in the relative link
        marketplace_link = f"https://workspace.google.com{add_on_element['href'][1:]}"

        add_on_data = ScrapeAddOnDetailsJob(
            url=marketplace_link,
            p_date=p_date,
            name=name,
            google_id=get_google_id_from_marketplace_link(marketplace_link),
            marketplace_link=marketplace_link,
        )
        result.append(add_on_data)

    print(f"found {len(result)} add_ons at {listing_url}")
    return result


def get_works_with_list(soup: BeautifulSoup) -> list:
    works_with_section = soup.find("div", class_="pBzYke")
    if works_with_section:
        return [
            div["aria-label"].replace("This app works with ", "")
            # Great, "eqVmXb" is used as ratingCount in 20210415205204
            for div in works_with_section.find_all("div", class_="eqVmXb")
        ]
    return []


def get_developer_link(soup: BeautifulSoup) -> Optional[str]:
    developer_link_element = soup.find("a", class_="DmgOFc Sm1toc")
    return developer_link_element["href"] if developer_link_element else None


def parse_permissions(soup) -> List[str]:
    permission_elements = soup.find_all("span", class_="jyBTLc")
    return [element.text.strip() for element in permission_elements]


@dataclass
class ReviewData:
    name: str
    stars: int
    content: str
    date_posted: str

    # For debugging
    def __str__(self):
        return f"{'⭐' * self.stars} {self.name} ({self.date_posted}): {self.content}"


# TODO(P3, completeness): This is actually paginated and the Google RPC looks super complicated to reverse engineer.
def parse_reviews(soup) -> List[ReviewData]:
    reviews = []
    review_elements = soup.find_all("div", class_="ftijEf")

    for element in review_elements:
        name = (
            element.find("div", class_="iLLAJe").text.strip()
            if element.find("div", class_="iLLAJe")
            else "No Name"
        )
        # Count SVG elements with stars
        stars = len(element.find_all("svg", tabindex="-1"))
        content = (
            element.find("div", class_="bR5MYb").text.strip()
            if element.find("div", class_="bR5MYb")
            else "No Content"
        )
        date_posted = (
            element.find("div", class_="wzBhKb").text.strip()
            if element.find("div", class_="wzBhKb")
            else "No Date"
        )

        reviews.append(
            ReviewData(name=name, stars=stars, content=content, date_posted=date_posted)
        )

    return reviews


def parse_rating_info(soup: BeautifulSoup) -> Tuple[Optional[float], Optional[int]]:
    rating_value_meta = soup.find("meta", itemprop="ratingValue")
    rating = float(rating_value_meta.get("content")) if rating_value_meta else None

    rating_count_span = soup.find("span", itemprop="ratingCount")
    rating_count = (
        extract_number_best_effort(rating_count_span.text)
        if rating_count_span
        else None
    )

    # The above should work, but sometimes this label has higher precision:
    average_rating_divs = soup.find_all(
        "div", attrs={"aria-label": lambda x: x and x.startswith("Average rating")}
    )
    if average_rating_divs:
        # Regular expression to extract the rating value
        rating_pattern = re.compile(r"Average rating:\s*([0-9.]+)")

        aria_label = average_rating_divs[0].get("aria-label", "")
        match = rating_pattern.search(aria_label)
        if match:
            rating = match.group(1)

    return rating, rating_count


def parse_downloads_count(soup: BeautifulSoup, debug_url: str) -> Optional[int]:
    # <div aria-label="457,795 users have installed this app.">457,795</div>
    user_div = soup.find(
        "div", {"aria-label": lambda x: x and "users have installed this app" in x}
    )
    if user_div:
        aria_label = user_div.get("aria-label", "")
        return int(extract_number_best_effort(aria_label.split(" ")[0]))

    # 20210509075544 (is missing that aria-label div)
    user_count_str = find_tag_and_get_text(soup, "div", "LCopac qlfxzd")
    user_count = extract_number_best_effort(user_count_str)
    if user_count == 0:
        print(
            f"WARNING: cannot find downloads_count_div LCopac NOR aria-label for url {debug_url}"
        )
    return int(user_count)


# TODO(P1, reliability): Consume all exceptions and keep on running the job
def process_add_on_page_response(
    scrape_job: ScrapeAddOnDetailsJob, add_on_html: str
) -> None:
    soup = BeautifulSoup(add_on_html, "html.parser")
    if not is_html_in_english(soup):
        # TODO(P3, performance): In an ideal world we should skip downloading this html with a row in the DB
        print(
            f"WARNING: page is not in English for {scrape_job.url}, rather skipping than getting wrong data."
        )
        return

    # This tag was there on 20210415205204
    # TODO(P2, reliability): This is a critical field, and will NOT work with de-listed apps.
    name = find_tag_and_get_text(soup, "span", "BfHp9b")

    # With "get_or_create" and later .save() we essentially get ON CONFLICT UPDATE (in two statements).
    add_on, created = GoogleWorkspace.get_or_create(
        google_id=scrape_job.google_id,
        p_date=scrape_job.p_date,
        name=name,
        link=scrape_job.marketplace_link,
    )
    if not created:
        print(
            f"INFO: will UPDATE existing GoogleWorkspace entry {add_on.p_date} {add_on.google_id}"
        )

    # For especially historical data, we want to keep the source URL for debugging / re-runs purposes.
    add_on.source_url = scrape_job.url

    save_large_fields = should_save_large_fields(scrape_job.p_date)
    _parse_add_on_page_response(
        add_on, soup, save_large_fields=save_large_fields, debug_url=scrape_job.url
    )

    # NOTE: yes this blocks the event loop and could benefit from asyncio,
    # but DB calls are usually way faster (3-10ms) than the HTTP GET (100-1000ms) above so it is fine.
    add_on.save()


def remove_endswith(text, suffix):
    if text.endswith(suffix):
        return text[: -len(suffix)].rstrip()
    return text


# TODO(P1, reliability): Maybe it's possible to parse the data from this Javascript stuff, unsure about Wayback though.
# <script nonce="">AF_initDataCallback({key: 'ds:1', hash: '6', data:[[428704666266,null,null,["Calamari","Modern leave and attendance management. Remote work, time off management and clock-in with iBeacons.","Calamari helps businesses and organizations boost the productivity of their employees by simplifying attendance and leave management. It's simple to use, allows tracking of vacation accrual and provides easy request and approval system for time off. It offers both attendance and leave tracking. Calamari automates time off approval and gives employees the easiest access to their leave records, useful PTO reports and team calendars overview.\n\nTry it for FREE! No credit card or commitment required.\nLeave Management:\n  • access control for different types of users (regular employees/managers/admins)\n  • PTO tracking, absence and vacation management, remote work tracking\n  • configuration of policies from different countries, custom leave types\n  • multilevel approval process, approval automation\n  • time off reports in Excel, PDF export\n  • team calendars, team capacity, absence calendar\n  • email notifications, slack notifications\n  • multi-country organizations\n  • requests on behalf of other employees (for managers)\n  • mobile app for employees and managers\n  • “who is off” weekly and daily notifications\n  • employee profiles \u0026 directory\n  • public API\n\nAttendance Management (clockin):\n  • attendance clock in methods: web browser, mobile application, QR codes, iBeacon, API\n  • mobile app with iBeacon technology\n  • abnormalities reporting\n  • working time reports, late arrivals and early departures reports\n  • reports export to payroll\n  • mobile application for employees\n  • real time attendance tracking\n  • clock in, clock out reminders\n  • time clock mobile terminals\n  • time tracking with GPS location\n  • clock in from email\n  • full history of changes made\n  • email notifications\n\n\nG Suite integration:\n  • synchronize employees from G Suite directory\n  • import employees for the onboarding\n  • import public holidays from Google calendar\n  • single sign on for G Suite users\n  • synchronize time off and remote work requests into Google Calendar\n  • available for multi-domain G Suite Accounts\n\nOther integrations:\n  • Slack (clock in / clock out / slack notifications)\n  • Atlassian JIRA (time off requests sync)\n  • Office 365/Outlook (time off calendar sync)\n\nQuality:\n  • dedicated subdomain, separate database\n  • support for all browsers and mobile devices\n  • 99.9% uptime and 24/7 monitoring\n  • hosting provider security: ISO 27001 CERT\n  • data backup in different availability zones\n  • English, Spanish, French, German, Polish language supported\n\nSee www.calamari.io for more details.","https://lh5.googleusercontent.com/-oLWY9PD6b5w/U_MVhYVsSCI/AAAAAAAAADQ/a33ioS_UCVY/s0/calamari_128x128_kolor.png","https://lh3.googleusercontent.com/9MReo6ZoloGfmb28DdImDYl_rubN6I1uukjUrjnN1ftlFYGe8H5qFskKi4qpXoReOFl33sXRNg\u003ds220-w220-h140-nd","calamari",[["https://lh3.googleusercontent.com/-pJaZMFzwk9g/ZC57WpfBGiI/AAAAAAAAAB0/nA2wLtxx-vIw24Y8nle1AHZfpowUgl60wCNcBGAsYHQ/s640-w640-h400/Ewidencja.png",1],["https://lh3.googleusercontent.com/-gOWhkaPJyqI/ZC57f1mpofI/AAAAAAAAAB8/DOiuaRHsQfILUfnWATbU4YMgFrvUEYw7gCNcBGAsYHQ/s640-w640-h400/Zegar.png",1],["https://lh3.googleusercontent.com/-HSPLNgQL4UM/ZC57jQ1jO1I/AAAAAAAAACE/xwFXiGPOEc8EB6Rx0YZ42-xU5Ld18J_ogCNcBGAsYHQ/s640-w640-h400/Manager.png",1],["https://lh3.googleusercontent.com/-UA9akNy7Etk/ZC57ltfKkQI/AAAAAAAAACM/y1N0sVa8brsEGDkb3C5ZdUmbNIsDlI17QCNcBGAsYHQ/s640-w640-h400/People%2Bdirectory.png",1],["https://lh3.googleusercontent.com/-aXmxFsrve2U/ZC57n19CsGI/AAAAAAAAACY/7_YEkviasxQQ2A3fskm4g-MwKA9xePhDwCNcBGAsYHQ/s640-w640-h400/Integracje.png",1]]],["calamari.io","",0,""],[10,5,"103K+",103974],null,null,["","https://calamari.io/terms-of-use","https://calamari.io/privacy-policy","https://help.calamari.io/","https://calamari.io/"],null,null,true,null,null,false,[[4,""]],null,false,false,null,2,[1680767910,147079000],2,false,null,false,null,[],false,false,false,""]], sideChannel: {}});</script>  #noqa
def _parse_add_on_page_response(
    add_on: GoogleWorkspace,
    soup: BeautifulSoup,
    save_large_fields: bool,
    debug_url=None,
):

    # They have changed styles and classes a few times, so we need to be careful here.
    # Observations:
    # * 20230307201612 has the "old" style
    # * 20230415205204 has the "new" style
    # Sometimes things got changed and then changed back - or maybe WebArchive has a bug.
    # TLDR; For historical data most important is to have the user_count, rating, rating_count tags.

    add_on.user_count = parse_downloads_count(soup=soup, debug_url=debug_url)

    # There are multiple of these, but the first one is the one we want
    developer_additional_info_span = soup.find("span", class_="nWIEC")
    if developer_additional_info_span:
        add_on.developer_name = developer_additional_info_span.text.strip()
        # A bit of a hack for <i class="google-material-icons bmrmhd" aria-hidden="true">open_in_new</i>,
        #   as in this case it is more nested in div/a/i
        add_on.developer_name = remove_endswith(add_on.developer_name, "open_in_new")
    else:
        developer_by = soup.find("div", class_="L6OhWc")
        if developer_by:
            add_on.developer_name = developer_by.text.replace("By:", "").strip()
            # A bit of a hack for <i class="google-material-icons bmrmhd" aria-hidden="true">open_in_new</i>,
            #   as in this case it is more nested in div/a/i
            add_on.developer_name = remove_endswith(
                add_on.developer_name, "open_in_new"
            )

    for developer_a in soup.find_all("a", class_="DmgOFc Sm1toc"):
        if (
            "plus.google.com" in developer_a["href"]
            or "support.google.com" in developer_a["href"]
        ):
            continue

        # Remove all subtags within the found <a> tag, this for .text to work correctly for subtags like:
        # <i class="google-material-icons bmrmhd" aria-hidden="true">open_in_new</i>
        for child_tag in developer_a.find_all(True):
            child_tag.decompose()
        add_on.developer_link = standardize_url(developer_a["href"])

        if add_on.developer_name is None:
            add_on.developer_name = developer_a.text.strip()

    if add_on.developer_name:
        add_on.developer_name = standardize_company_name(add_on.developer_name)

    add_on.rating, add_on.rating_count = parse_rating_info(soup=soup)
    if add_on.rating is None or add_on.rating_count is None:
        print(f"WARNING: cannot parse rating or rating count for url {debug_url}")

    listing_updated_str = find_tag_and_get_text(soup, "div", "bVxKXd").replace(
        "Listing updated:", ""
    )
    add_on.listing_updated = listing_updated_str_to_date(listing_updated_str)
    add_on.description = find_tag_and_get_text(soup, "div", "kmwdk")
    add_on.pricing = find_tag_and_get_text(soup, "span", "P0vMD")
    add_on.fill_in_works_with(get_works_with_list(soup=soup))
    if save_large_fields:
        add_on.overview = find_tag_and_get_text(soup, "pre", "nGA4ed")

    img_logo_tag = soup.find("img", class_="TS9dEf")
    add_on.logo_link = img_logo_tag.get("src") if img_logo_tag else None
    featured_img_tag = soup.find("img", class_="ec1OGc")
    add_on.featured_img_link = featured_img_tag.get("src") if featured_img_tag else None

    if save_large_fields:
        add_on.permissions = parse_permissions(soup=soup)
    add_on.reviews = parse_reviews(soup=soup)


async def async_scrape_add_on_details(
    scrape_job: ScrapeAddOnDetailsJob, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        print(f"getting more add_on data for {scrape_job.name} from {scrape_job.url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(scrape_job.url) as response:
                if response.status != 200:
                    print("WARNING: could not get data")
                    return
                add_on_html = await response.text()
                # TODO(P0, scraping): Try instead https://github.com/unclecode/crawl4ai ; BUT likely expensive
                process_add_on_page_response(scrape_job, add_on_html)


# A backup version for async_research_app_more, sometimes makes it easier to debug.
def sync_scrape_add_on_details(scrape_job: ScrapeAddOnDetailsJob) -> None:
    print(f"getting more add_on data for {scrape_job.name} from {scrape_job.url}")
    response = requests.get(scrape_job.url)
    if response.status_code != 200:
        print("WARNING: could not get data")
        return

    process_add_on_page_response(scrape_job, add_on_html=response.text)


def get_all_from_marketplace(p_date: str) -> List[ScrapeAddOnDetailsJob]:
    result = {}

    for listing_page in LISTS:
        scrape_jobs = get_add_ons_from_listing_page(listing_page, p_date=p_date)

        result.update(
            {scrape_job.marketplace_link: scrape_job for scrape_job in scrape_jobs}
        )

    return list(result.values())


def get_all_google_workspace_from_database(p_date: str) -> List[ScrapeAddOnDetailsJob]:
    # Define the subquery to get the latest p_date for each google_id
    subquery = (
        GoogleWorkspace.select(
            GoogleWorkspace.google_id,
            fn.MAX(GoogleWorkspace.p_date).alias("max_p_date"),
        )
        .group_by(GoogleWorkspace.google_id)
        .alias("subquery")
    )

    # Join the subquery with the original table to get the source_url
    query = GoogleWorkspace.select(
        GoogleWorkspace.google_id,
        GoogleWorkspace.source_url,
        GoogleWorkspace.link.GoogleWorkspace.name,
    ).join(
        subquery,
        on=(
            (GoogleWorkspace.google_id == subquery.c.google_id)
            & (GoogleWorkspace.p_date == subquery.c.max_p_date)
        ),
    )

    # Execute the query and fetch the results
    result = []
    for entry in query:
        result.append(
            ScrapeAddOnDetailsJob(
                url=entry.source_url if entry.source_url else entry.link,
                p_date=p_date,
                name=entry.name,
                google_id=entry.google_id,
                marketplace_link=entry.link,
            )
        )
    return result


async def scrape_google_workspace_add_ons(
    scrape_jobs: List[ScrapeAddOnDetailsJob],
) -> None:
    print(f"will run HTTP GET Details with {ASYNC_IO_MAX_PARALLELISM} parallelism")
    tasks = []
    semaphore = asyncio.Semaphore(ASYNC_IO_MAX_PARALLELISM)

    for scrape_job in scrape_jobs:
        # Schedule the task with semaphore
        task = async_scrape_add_on_details(scrape_job=scrape_job, semaphore=semaphore)
        tasks.append(asyncio.create_task(task))
        # sync_research_add_on_more(add_on)

    # Await all tasks to complete
    print(f"INFO: Main 'thread' waiting on all {len(tasks)} asyncio tasks START")
    await asyncio.gather(*tasks)
    print("INFO: Main 'thread' waiting on all asyncio tasks DONE")


def main():
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        # scrape_job_list = get_all_from_marketplace(p_date)
        # asyncio.run(scrape_google_workspace_add_ons(scrape_job_list))
        # get_all_google_workspace_add_ons(p_date)

        test_job = ScrapeAddOnDetailsJob(
            url="https://web.archive.org/web/20210415205204id_/https://workspace.google.com/marketplace/app/merge_values/857144221591",
            p_date="2021-04-15",
            name=None,
            google_id="857144221591",
            marketplace_link="https://workspace.google.com/marketplace/app/merge_values/857144221591",
        )
        process_add_on_page_response(test_job, requests.get(test_job.url).text)


if __name__ == "__main__":
    main()
