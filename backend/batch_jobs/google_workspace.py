# TODO(P1, feature:trends): Can get historical data through WayBack
#  curl "http://archive.org/wayback/available?url=<LINK>&timestamp=20240101" | jq .
#  https://web.archive.org/web/20231101062549/https://workspace.google.com/marketplace/app/mail_merge/218858140171
import asyncio
import urllib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote

import aiohttp
import requests
from bs4 import BeautifulSoup
from supawee.client import connect_to_postgres

from batch_jobs.common import (
    ASYNC_IO_MAX_PARALLELISM,
    find_tag_and_get_text,
    listing_updated_str_to_date,
    parse_shortened_int_k_m,
)
from batch_jobs.search_terms import GOOGLE_WORKSPACE_SEARCH_TERMS
from common.config import POSTGRES_DATABASE_URL
from supabase.models.data import GoogleAddOn

# TODO(P0, completeness): Figure out a way to crawl the entire site,
#  note that https://workspace.google.com/marketplace/sitemap.xml isn't enough
#  Currently best effort by categories and keywords.
SEARCH_URL = "https://workspace.google.com/marketplace/search/"

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


@dataclass
class AddOnDataBasic:
    name: str
    developer_name: str
    rating: str
    rating_count: int
    user_count: int
    link: str


def get_add_ons_from_listing_page(url: str) -> List[AddOnDataBasic]:
    print(f"getting add_ons from {url}")
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"WARNING: cannot fetch data from url {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    add_on_elements = soup.find_all("a", class_="RwHvCd")
    result = []
    for add_on_element in add_on_elements:
        add_on_name = find_tag_and_get_text(add_on_element, "div", "M0atNd")
        user_span = add_on_element.find("span", class_="kVdtk")
        user_span_sibling = user_span.find_next_sibling("span") if user_span else None
        if user_span_sibling is not None:
            user_count = parse_shortened_int_k_m(user_span_sibling.text.strip())
        else:
            print(
                f"WARNING: cannot find user span or user span sibling for url {url} and add_on {add_on_name}"
            )
            user_count = None

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        add_on_data = AddOnDataBasic(
            name=add_on_name,
            developer_name=find_tag_and_get_text(add_on_element, "span", "y51Cnd"),
            rating=find_tag_and_get_text(add_on_element, "span", "wUhZA"),
            rating_count=0,  # will be updated
            user_count=user_count,
            # [1:] removes the first dot in the relative link
            link=f"https://workspace.google.com{add_on_element['href'][1:]}",
        )
        result.append(add_on_data)

    print(f"found {len(result)} add_ons at {url}")
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


def process_add_on_page_response(add_on: GoogleAddOn, add_on_html: str) -> None:
    soup = BeautifulSoup(add_on_html, "html.parser")

    rating_count_el = soup.find("span", itemprop="ratingCount")
    add_on.rating_count = (
        str_to_int_safe(rating_count_el.text)
        if rating_count_el
        else add_on.rating_count
    )
    listing_updated_str = find_tag_and_get_text(soup, "div", "bVxKXd").replace(
        "Listing updated:", ""
    )
    add_on.listing_updated = listing_updated_str_to_date(listing_updated_str)
    add_on.description = find_tag_and_get_text(soup, "div", "kmwdk")
    add_on.pricing = find_tag_and_get_text(soup, "span", "P0vMD")
    add_on.fill_in_works_with(get_works_with_list(soup=soup))
    # TODO: gpt to summarize - probably in another script
    add_on.overview = find_tag_and_get_text(soup, "pre", "nGA4ed")

    img_logo_tag = soup.find("img", class_="TS9dEf")
    add_on.logo_link = img_logo_tag.get("src") if img_logo_tag else None
    featured_img_tag = soup.find("img", class_="ec1OGc")
    add_on.featured_img_link = featured_img_tag.get("src") if featured_img_tag else None

    add_on.developer_link = get_developer_link(soup=soup)
    add_on.permissions = parse_permissions(soup=soup)
    add_on.reviews = parse_reviews(soup=soup)
    # add_on.display()


async def async_research_add_on_more(
    add_on: GoogleAddOn, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        print(f"getting more add_on data for {add_on.name} from {add_on.link}")
        async with aiohttp.ClientSession() as session:
            async with session.get(add_on.link) as response:
                if response.status != 200:
                    print("WARNING: could not get data")
                    return
                add_on_html = await response.text()
                process_add_on_page_response(add_on, add_on_html)
                # NOTE: yes this blocks the event loop and could benefit from asyncio,
                # but DB calls are usually way faster (3-10ms) than the HTTP GET (100-1000ms) above so it is fine.
                add_on.save()


# A backup version for async_research_app_more, sometimes makes it easier to debug.
def sync_research_add_on_more(add_on: GoogleAddOn) -> None:
    print(f"getting more app data for {add_on.name} from {add_on.link}")
    response = requests.get(add_on.link)
    if response.status_code != 200:
        print("WARNING: could not get data")
        return

    process_add_on_page_response(add_on, add_on_html=response.text)
    add_on.save()


def get_add_on_id_from_link(link: str):
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


async def get_all_google_workspace_add_ons(p_date: str):
    researched_add_ons = set()
    print(
        f"will run individual add_on HTTP GET with {ASYNC_IO_MAX_PARALLELISM} max parallelism"
    )
    tasks = []
    semaphore = asyncio.Semaphore(ASYNC_IO_MAX_PARALLELISM)

    for listing_page in LISTS:
        add_ons = get_add_ons_from_listing_page(listing_page)
        for add_on_data in add_ons:
            link = add_on_data.link
            if link in researched_add_ons:
                continue
            researched_add_ons.add(link)

            # With "get_or_create" and later .save() we essentially get ON CONFLICT UPDATE (in two statements).
            add_on, created = GoogleAddOn.get_or_create(
                google_id=get_add_on_id_from_link(link),
                p_date=p_date,
                name=add_on_data.name,
                link=add_on_data.link,
            )
            add_on.developer_name = add_on_data.developer_name
            add_on.rating = add_on_data.rating
            add_on.rating_count = add_on_data.rating_count
            add_on.user_count = add_on_data.user_count

            # TODO(P1, reliability): Quite often I have troubles killing this script.
            # Schedule the task with semaphore
            task = async_research_add_on_more(add_on, semaphore)
            tasks.append(asyncio.create_task(task))
            # sync_research_add_on_more(add_on)

    # Await all tasks to complete
    print(f"INFO: Main 'thread' waiting on all {len(tasks)} asyncio tasks START")
    await asyncio.gather(*tasks)
    print("INFO: Main 'thread' waiting on all asyncio tasks DONE")


if __name__ == "__main__":
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        asyncio.run(get_all_google_workspace_add_ons(p_date))
        # get_all_google_workspace_add_ons(p_date)
