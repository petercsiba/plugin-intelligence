# TODO(P0, quality): Get the full Chrome Extension list from Kaggle, and adjust daily scraper to use the DB too.
# TODO(P1, ops): At some point we will need to upscale the scraping beyond marketplaces, to the whole web.
#   This is a project in itself, check out what this guy writes (also has a GPT web scraping article)
#   https://medium.com/@macrodrigues/web-scraping-with-scrapy-and-splash-3d5666ba78ff
import asyncio
import re
import urllib
from dataclasses import dataclass
from datetime import datetime
from typing import List
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
from batch_jobs.scraper.search_terms import CHROME_EXTENSION_SEARCH_TERMS
from common.config import POSTGRES_DATABASE_URL
from supabase.models.data import ChromeExtension

SEARCH_URL = "https://chromewebstore.google.com/search/"
# The "minimalRating=5" filter usually gets the newer / less popular ones as it's impossible to maintain only fives.
LISTS = (
    [
        SEARCH_URL + quote(term) + "?minimalRating=5"
        for term in CHROME_EXTENSION_SEARCH_TERMS
    ]
    + [SEARCH_URL + quote(term) for term in CHROME_EXTENSION_SEARCH_TERMS]
    + [
        "https://chromewebstore.google.com/category/extensions/productivity/communication",
        "https://chromewebstore.google.com/category/extensions/productivity/communication?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/productivity/developer",
        "https://chromewebstore.google.com/category/extensions/productivity/developer?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/productivity/education",
        "https://chromewebstore.google.com/category/extensions/productivity/education?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/productivity/tools",
        "https://chromewebstore.google.com/category/extensions/productivity/tools?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/productivity/workflow",
        "https://chromewebstore.google.com/category/extensions/productivity/workflow?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/art",
        "https://chromewebstore.google.com/category/extensions/lifestyle/art?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/entertainment",
        "https://chromewebstore.google.com/category/extensions/lifestyle/entertainment?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/games",
        "https://chromewebstore.google.com/category/extensions/lifestyle/games?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/household",
        "https://chromewebstore.google.com/category/extensions/lifestyle/household?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/fun",
        "https://chromewebstore.google.com/category/extensions/lifestyle/fun?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/news",
        "https://chromewebstore.google.com/category/extensions/lifestyle/news?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/shopping",
        "https://chromewebstore.google.com/category/extensions/lifestyle/shopping?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/social",
        "https://chromewebstore.google.com/category/extensions/lifestyle/social?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/travel",
        "https://chromewebstore.google.com/category/extensions/lifestyle/travel?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/lifestyle/well_being",
        "https://chromewebstore.google.com/category/extensions/lifestyle/well_being?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/accessibility",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/accessibility?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/functionality",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/functionality?sortBy=highestRated",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/privacy",
        "https://chromewebstore.google.com/category/extensions/make_chrome_yours/privacy?sortBy=highestRated",
    ]
)


@dataclass
class ExtensionDataBasic:
    name: str
    rating: str
    rating_count: int
    link: str
    description: str


def get_extensions_from_category_page(url: str) -> List[ExtensionDataBasic]:
    print(f"getting chrome extension from {url} (assuming category page)")
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"WARNING: cannot fetch data from url {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    extension_elements = soup.find_all("div", class_="cD9yc")

    result = []
    for extension_element in extension_elements:
        extension_name = find_tag_and_get_text(extension_element, "p", "GzKZcb")
        print(f"parsing extension {extension_name}")
        rating_count_span = find_tag_and_get_text(extension_element, "span", "Y30PE")
        rating_count = parse_shortened_int_k_m(
            rating_count_span.replace(")", "").replace("(", "").strip()
        )
        link_span = extension_element.find("a", class_="UvhDdd")

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        extension_data = ExtensionDataBasic(
            name=extension_name,
            rating=find_tag_and_get_text(extension_element, "span", "Vq0ZA"),
            rating_count=rating_count,
            # [1:] removes the first dot in the relative link
            link=f"https://chromewebstore.google.com{link_span['href'][1:]}",
            description=find_tag_and_get_text(extension_element, "p", "Uufqmb"),
        )
        result.append(extension_data)

    print(f"found {len(result)} chrome extensions at {url}")
    return result


def get_extensions_from_search_page(url: str) -> List[ExtensionDataBasic]:
    print(f"getting chrome extension from {url} (assuming search page)")
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"WARNING: cannot fetch data from url {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    extension_elements = soup.find_all("div", class_="Cb7Kte")

    result = []
    for extension_element in extension_elements:
        extension_name = find_tag_and_get_text(extension_element, "h2", "CiI2if")
        # print(f"parsing extension {extension_name}")
        rating_count_span = find_tag_and_get_text(extension_element, "span", "Y30PE")
        rating_count = parse_shortened_int_k_m(
            rating_count_span.replace(")", "").replace("(", "").strip()
        )
        link_span = extension_element.find("a", class_="q6LNgd")

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        extension_data = ExtensionDataBasic(
            name=extension_name,
            rating=find_tag_and_get_text(extension_element, "span", "Vq0ZA"),
            rating_count=rating_count,
            # [1:] removes the first dot in the relative link
            link=f"https://chromewebstore.google.com{link_span['href'][1:]}",
            description=find_tag_and_get_text(extension_element, "p", "g3IrHd"),
        )
        result.append(extension_data)

    print(f"found {len(result)} chrome extensions at {url}")
    return result


def get_extensions(url: str) -> List[ExtensionDataBasic]:
    if "/search/" in url:
        return get_extensions_from_search_page(url)

    return get_extensions_from_category_page(url)


# TODO(P2, devx): Cleanliness would dictate to reuse the one in Google Workspace
async def async_research_extension_more(
    chrome_extension: ChromeExtension, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        print(
            f"getting more extension data for {chrome_extension.name} from {chrome_extension.link}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(chrome_extension.link) as response:
                if response.status != 200:
                    print("WARNING: could not get data")
                    return
                extension_html = await response.text()
                process_extension_page_response(chrome_extension, extension_html)
                # NOTE: yes this blocks the event loop and could benefit from asyncio,
                # but DB calls are usually way faster (3-10ms) than the HTTP GET (100-1000ms) above so it is fine.
                chrome_extension.save()


def process_extension_page_response(
    chrome_extension: ChromeExtension, extension_html: str
):
    soup = BeautifulSoup(extension_html, "html.parser")

    chrome_extension.name = find_tag_and_get_text(soup, "h1", "Pa2dE")
    chrome_extension.landing_page_url = find_tag_and_get_text(soup, "a", "cJI8ee")
    chrome_extension.is_featured = soup.find("span", class_="OmOMFc") is not None

    img_logo_tag = soup.find("img", class_="rBxtY")
    chrome_extension.logo_link = img_logo_tag.get("src") if img_logo_tag else None
    featured_img_tag = soup.find("img", class_="VuCTZc")
    chrome_extension.featured_img_link = featured_img_tag.get("src") if featured_img_tag else None

    category_and_users_tag = soup.find("div", class_="F9iKBc")
    chrome_extension.categories = [
        category_tag.text for category_tag in category_and_users_tag.find_all("a")
    ]
    chrome_extension.user_count = parse_shortened_int_k_m(
        re.sub("[^0-9]", "", category_and_users_tag.text)
    )

    overview_div = soup.find("div", class_="uORbKe")
    chrome_extension.overview = "\n".join(
        [p_tag.text for p_tag in overview_div.find_all("p")]
    )

    chrome_extension.released_version = find_tag_and_get_text(soup, "div", "pDlpAd")

    listing_updated_li = soup.find("li", class_="kBFnc")
    listing_updated_str = " ".join(
        [div_tag.text for div_tag in listing_updated_li.find_all("div")]
    )
    chrome_extension.listing_updated = listing_updated_str_to_date(
        listing_updated_str.replace("Updated", "").strip()
    )

    chrome_extension.developer_name = find_tag_and_get_text(soup, "div", "C2WXF")
    developer_link_a = soup.find("a", "XQ8Hh")
    chrome_extension.developer_link = (
        developer_link_a.get("href") if developer_link_a else None
    )
    chrome_extension.developer_email = find_tag_and_get_text(soup, "div", "yNyGQd")

    chrome_extension.permissions = [
        span_tag.text for span_tag in soup.find_all("span", "PuNHYb")
    ]

    # TODO(P2, feature): Review text from chrome_extension.link + "/reviews


# looks like bmnlcjabgnpnenekpadlanbbkooimhnj
def get_extension_id_from_link(link: str) -> str:
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


async def get_all_chrome_extensions(p_date: str) -> None:
    researched_extensions = set()
    print(
        f"will run individual app HTTP GET with {ASYNC_IO_MAX_PARALLELISM} max parallelism"
    )

    # for listing_page in LISTS:
    for listing_page in LISTS:
        extensions = get_extensions(listing_page)

        tasks = []
        semaphore = asyncio.Semaphore(ASYNC_IO_MAX_PARALLELISM)

        for extension_data in extensions:
            # Already visited? In-memory version
            link = extension_data.link
            if link in researched_extensions:
                continue
            researched_extensions.add(link)

            # Already visited? In-database version. NOTE: to re-scrape this needs to be removed
            google_id = get_extension_id_from_link(link)
            exists = (
                ChromeExtension.select()
                .where(
                    (ChromeExtension.google_id == google_id)
                    & (ChromeExtension.p_date == p_date)
                )
                .exists()
            )
            if exists:
                continue

            # With "get_or_create" and later .save() we essentially get ON CONFLICT UPDATE (in two statements).
            # TODO(P2, correctness): get_or_create doesn't work when unique key is (google_id, p_date) and more
            # columns.
            chrome_extension, created = ChromeExtension.get_or_create(
                google_id=google_id,
                p_date=p_date,
                name=extension_data.name,
                link=extension_data.link,
            )
            chrome_extension.rating = extension_data.rating
            chrome_extension.rating_count = extension_data.rating_count
            chrome_extension.description = extension_data.description

            # Schedule the task with semaphore
            task = async_research_extension_more(chrome_extension, semaphore)
            tasks.append(asyncio.create_task(task))
            # sync_research_extension_more(chrome_extension)

        if len(tasks) > 0:
            print(
                f"INFO: Main 'thread' waiting on all {len(tasks)} asyncio tasks START"
            )
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        asyncio.run(get_all_chrome_extensions(p_date))
