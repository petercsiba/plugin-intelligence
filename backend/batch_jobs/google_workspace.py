# TODO(P1, feature:trends): Can get historical data through WayBack
#  curl "http://archive.org/wayback/available?url=<LINK>&timestamp=20240101" | jq .
#  https://web.archive.org/web/20231101062549/https://workspace.google.com/marketplace/app/mail_merge/218858140171
import asyncio
import re
import urllib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote

import aiohttp
import requests
from bs4 import BeautifulSoup, Tag
from supawee.client import connect_to_postgres

from config import POSTGRES_DATABASE_URL
from supabase.models.data import GoogleAddOn

# How many concurrent HTTP GET can run in the scraper. The ideal here depends on the provisioned machine,
# and how the scraper target domain is sensitive. This is a super-basic scraper, but if it ain't working
# might make sense to use a library / service.
ASYNC_IO_MAX_PARALLELISM = 6

# TODO(P0, completeness): Figure out a way to crawl the entire site,
#  note that https://workspace.google.com/marketplace/sitemap.xml isn't enough
#  Currently best effort by categories and keywords.
SEARCH_URL = "https://workspace.google.com/marketplace/search/"
# These are often used keywords
KEYWORDS = [
    # data pipelines
    "data",
    "connector",
    "export",
    "import",
    "database",
    "merge",
    "api",
    "sync",
    "zapier",
    "stitchdata",
    "fivetran",
    # general productivity
    "email",
    "mail merge",
    "calendar",
    "docs",
    "sheets",
    "slides",
    "reports",
    "diagram",
    "forms",
    "trello",
    "quiz",
    "automatic",
    # ADS
    "ads",
    "analytics",
    "social",
    "seo",
    "ppc",
    "facebook",
    "linkedin",
    "snapchat",
    # E-commerce
    "e-commerce",
    "shopify",
    "qr",
    # CRM
    "crm",
    "contacts",
    "salesforce",
    "hubspot",
    "zoho",
    # File management
    "pdf",
    "zip",
    "sign",
    "docusign",
    "encrypt",
    "secure",
    # Finance
    "finance",
    "accounting",
    "quickbooks",
    "stocks",
    "trading",
    # AI
    "gpt",
    "chatgpt",
    "ai",
    "translate",
    "transcribe",
]

TEST_LIST = ["https://workspace.google.com/marketplace"]
LISTS = [SEARCH_URL + quote(term) for term in KEYWORDS] + [
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


def find_tag_and_get_text(element: Tag, tag_name: str, class_name: str) -> str:
    found_element = element.find(tag_name, class_=class_name)
    return found_element.text.strip() if found_element else ""


# parse_user_count converts strings like '4K' to '4000' and '1M' to '1000000'
def parse_user_count(user_str: str) -> int:
    multiplier = {"K": 1000, "M": 1000000}
    match = re.search(r"(\d+)([KM])", user_str)
    if match:
        number = int(match.group(1))
        suffix = match.group(2)
        return number * multiplier[suffix]
    return int(user_str)  # Might error out?


@dataclass
class AppDataBasic:
    name: str
    developer_name: str
    rating: str
    rating_count: int
    user_count: int
    link: str


def get_apps(url: str) -> List[AppDataBasic]:
    print(f"getting apps from {url}")
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"WARNING: cannot fetch data from url {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    apps = soup.find_all("a", class_="RwHvCd")
    result = []
    for app in apps:
        app_name = find_tag_and_get_text(app, "div", "M0atNd")
        user_span = app.find("span", class_="kVdtk")
        user_span_sibling = user_span.find_next_sibling("span") if user_span else None
        if user_span_sibling is not None:
            user_count = parse_user_count(user_span_sibling.text.strip())
        else:
            print(
                f"WARNING: cannot find user span or user span sibling for url {url} and app {app_name}"
            )
            user_count = None

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        app_data = AppDataBasic(
            name=app_name,
            developer_name=find_tag_and_get_text(app, "span", "y51Cnd"),
            rating=find_tag_and_get_text(app, "span", "wUhZA"),
            rating_count=0,  # will be updated
            user_count=user_count,
            # [1:] removes the first dot in the relative link
            link=f"https://workspace.google.com{app['href'][1:]}",
        )
        result.append(app_data)

    print(f"found {len(result)} apps at {url}")
    return result


def get_works_with_list(soup: BeautifulSoup) -> list:
    works_with_section = soup.find("div", class_="pBzYke")
    if works_with_section:
        return [
            div["aria-label"].replace("This app works with ", "")
            for div in works_with_section.find_all("div", class_="eqVmXb")
        ]
    return []


def get_developer_link(soup: BeautifulSoup) -> Optional[str]:
    developer_link_element = soup.find("a", class_="DmgOFc Sm1toc")
    return developer_link_element["href"] if developer_link_element else None


@dataclass
class ReviewData:
    name: str
    stars: int
    content: str
    date_posted: str

    # For debugging
    def __str__(self):
        return f"{'⭐' * self.stars} {self.name} ({self.date_posted}): {self.content}"


def parse_permissions(soup) -> List[str]:
    permission_elements = soup.find_all("span", class_="jyBTLc")
    return [element.text.strip() for element in permission_elements]


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


def str_to_int_safe(int_str: str) -> int:
    try:
        return int(int_str.strip().replace(",", "").replace("$", ""))
    except ValueError as e:
        print(f"INFO: cannot convert {int_str} to int cause {e}")


def process_app_page_response(add_on: GoogleAddOn, text: str) -> None:
    soup = BeautifulSoup(text, "html.parser")

    rating_count_el = soup.find("span", itemprop="ratingCount")
    add_on.rating_count = (
        str_to_int_safe(rating_count_el.text)
        if rating_count_el
        else add_on.rating_count
    )
    listing_updated_str = find_tag_and_get_text(soup, "div", "bVxKXd").replace(
        "Listing updated:", ""
    )
    try:
        add_on.listing_updated = datetime.strptime(
            listing_updated_str, "%B %d, %Y"
        ).date()  # "April 24, 2024"
    except ValueError as e:
        if len(listing_updated_str) > 2:
            print(
                f"info: cannot parse listing updated for {listing_updated_str} cause: {e}"
            )
    add_on.description = find_tag_and_get_text(soup, "div", "kmwdk")
    add_on.pricing = find_tag_and_get_text(soup, "span", "P0vMD")
    # app_data.works_with = get_works_with(app=soup)
    add_on.fill_in_works_with(get_works_with_list(soup=soup))
    # TODO: gpt to summarize - probably in another script
    add_on.overview = find_tag_and_get_text(soup, "pre", "nGA4ed")
    add_on.developer_link = get_developer_link(soup=soup)
    add_on.permissions = parse_permissions(soup=soup)
    add_on.reviews = parse_reviews(soup=soup)
    # app_data.display()


async def async_research_app_more(
    add_on: GoogleAddOn, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        print(f"getting more app data for {add_on.name} from {add_on.link}")
        async with aiohttp.ClientSession() as session:
            async with session.get(add_on.link) as response:
                if response.status != 200:
                    print("WARNING: could not get data")
                    return
                data = await response.text()
                process_app_page_response(add_on, data)
                # NOTE: yes this blocks the event loop and could benefit from asyncio,
                # but DB calls are usually way faster (3-10ms) than the HTTP GET (100-1000ms) above so it is fine.
                add_on.save()


# A backup version for async_research_app_more, sometimes makes it easier to debug.
def sync_research_app_more(add_on: GoogleAddOn) -> None:
    print(f"getting more app data for {add_on.name} from {add_on.link}")
    response = requests.get(add_on.link)
    if response.status_code != 200:
        print("WARNING: could not get data")
        return

    process_app_page_response(add_on, response.text)
    add_on.save()


def get_google_id_from_link(link: str):
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


async def main():
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")

    with connect_to_postgres(POSTGRES_DATABASE_URL):
        # TODO(P1, prod): Using some real scraper library might be helpful,
        #   and concurrency / asyncio welcome since most time is spent waiting on HTTP GET requests.
        researched_apps = set()
        print(
            f"will run individual app HTTP GET with {ASYNC_IO_MAX_PARALLELISM} max parallelism"
        )
        tasks = []
        semaphore = asyncio.Semaphore(
            ASYNC_IO_MAX_PARALLELISM
        )  # Allow up to 10 concurrent tasks

        # for listing_page in LISTS:
        for listing_page in TEST_LIST:
            apps = get_apps(listing_page)
            for app_data in apps:
                link = app_data.link
                if link in researched_apps:
                    continue
                researched_apps.add(link)

                # With "get_or_create" and later .save() we essentially get ON CONFLICT UPDATE (in two statements).
                add_on, created = GoogleAddOn.get_or_create(
                    google_id=get_google_id_from_link(link),
                    p_date=p_date,
                    name=app_data.name,
                    link=app_data.link,
                )
                add_on.developer_name = app_data.developer_name
                add_on.rating = app_data.rating
                add_on.rating_count = app_data.rating_count
                add_on.user_count = app_data.user_count

                # Schedule the task with semaphore
                task = async_research_app_more(add_on, semaphore)
                tasks.append(asyncio.create_task(task))
                # sync_research_app_more(add_on)

        # Await all tasks to complete
        print("INFO: Main 'thread' waiting on all asyncio tasks START")
        await asyncio.gather(*tasks)
        print("INFO: Main 'thread' waiting on all asyncio tasks DONE")


if __name__ == "__main__":
    asyncio.run(main())
    # main()
