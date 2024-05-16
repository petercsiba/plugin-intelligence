# TODO(P0, quality): Get the full Chrome Extension list from Kaggle, and adjust daily scraper to use the DB too.
# TODO(P1, ops): At some point we will need to upscale the scraping beyond marketplaces, to the whole web.
#   This is a project in itself, check out what this guy writes (also has a GPT web scraping article)
#   https://medium.com/@macrodrigues/web-scraping-with-scrapy-and-splash-3d5666ba78ff
import asyncio
import re
import urllib
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import quote, urlparse

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
    is_html_in_english, standardize_url,
)
from batch_jobs.scraper.search_terms import CHROME_EXTENSION_SEARCH_TERMS
from batch_jobs.scraper.settings import should_save_large_fields
from common.config import POSTGRES_DATABASE_URL
from supabase.models.data import ChromeExtension

SEARCH_URL = "https://chromewebstore.google.com/search/"
# The "minimalRating=5" filter usually gets the newer / less popular ones as it's impossible to maintain only fives.
LISTS = (
    [
        SEARCH_URL + quote(term) + "?sortBy=highestRated"
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


class ScrapeChromeExtensionJob(BaseModel):
    # can either be a marketplace_link OR wayback url
    # NOTE: The slug part of URL is only for SEO, you can put anything there
    # https://chromewebstore.google.com/detail/HELLO-WORLD-HAHAHA/fheoggkfdfchfphceeifdbepaooicaho
    url: str
    # Y-m-d, also determines the format of the data to be scraped
    p_date: str
    # Part of Unique Key
    google_id: str

    # Optional stuff to help with the scraping
    name: Optional[str] = None
    marketplace_link: Optional[str] = None


def get_marketplace_link(soup: BeautifulSoup) -> str:
    # They seem to re-use the same class names across different page types
    link_span = soup.find("a", class_="UvhDdd")
    # [1:] removes the first dot in the relative link
    return f"https://chromewebstore.google.com{link_span['href'][1:]}"


def get_extensions_from_category_page(url: str, p_date: str) -> List[ScrapeChromeExtensionJob]:
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
        marketplace_link = get_marketplace_link(extension_element)

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        extension_data = ScrapeChromeExtensionJob(
            url=marketplace_link,
            p_date=p_date,
            # Optional stuff
            name=extension_name,
            google_id=get_extension_id_from_link(marketplace_link),
            marketplace_link=marketplace_link,
        )
        result.append(extension_data)

    print(f"found {len(result)} chrome extensions at {url}")
    return result


def get_extensions_from_search_page(url: str, p_date: str) -> List[ScrapeChromeExtensionJob]:
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
        marketplace_link = get_marketplace_link(extension_element)

        # description = find_tag_and_get_text(extension_element, "p", "g3IrHd"),
        # Fill in the data available from the listings table page, more will be filled from individual pages.
        extension_data = ScrapeChromeExtensionJob(
            url=marketplace_link,
            p_date=p_date,
            # Optional stuff
            name=extension_name,
            google_id=get_extension_id_from_link(marketplace_link),
            marketplace_link=marketplace_link,
        )
        result.append(extension_data)

    print(f"found {len(result)} chrome extensions at {url}")
    return result


def get_extensions_from_listing_page(url: str, p_date: str) -> List[ScrapeChromeExtensionJob]:
    if "/search/" in url:
        return get_extensions_from_search_page(url, p_date=p_date)

    return get_extensions_from_category_page(url, p_date=p_date)


# Yeah, there libraries for this BUT I want more control and transparency.
async def fetch_with_retry(url: str, params=None, retry_limit=3) -> Tuple[Optional[str], Optional[str]]:
    retry_count = 0

    while retry_count < retry_limit:
        print("chrome extension fetch_with_retry", url, params, retry_count)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, allow_redirects=True) as response:
                    if response.status == 200:
                        extension_html = await response.text()
                        return extension_html, str(response.url)
                    else:
                        print(f"ERROR: could not get data, status code: {response.status}")
                        return None, None
        except (aiohttp.ClientConnectorError, aiohttp.client.ClientConnectionError) as e:
            sleep_time = 70 * 2**retry_count
            retry_count += 1
            print(f"ClientConnectorError {e}")
            print(f"Sleeping {sleep_time} seconds and retrying {url}")
            await asyncio.sleep(sleep_time)

    return None, None


# TODO(P2, devx): Cleanliness would dictate to reuse the one in Google Workspace
async def async_research_extension_more(
    scrape_job: ScrapeChromeExtensionJob, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        response_text, response_url = await fetch_with_retry(scrape_job.url)
        if response_text is None:
            print(f"ERROR: cannot fetch data from url {scrape_job.url}")

        if "https://archive.org" not in response_url:
            # In case of redirects, which happen when we do not know the exact URL
            print(f"marketplace_link updated to {response_url}")
            scrape_job.marketplace_link = response_url

        process_extension_page_response(scrape_job, response_text)


def parse_listing_updated(soup: BeautifulSoup, chrome_extension: ChromeExtension):
    listing_updated_li = soup.find("li", class_="kBFnc")
    if listing_updated_li is None:
        listing_updated_li = soup.find("li", class_="ZbWJPd uBIrad")
    if listing_updated_li:
        listing_updated_str = " ".join(
            [div_tag.text for div_tag in listing_updated_li.find_all("div")]
        )
        chrome_extension.listing_updated = listing_updated_str_to_date(
            listing_updated_str.replace("Updated", "").strip()
        )
    else:
        print(f"WARNING: cannot find listing updated for {chrome_extension.source_url}")


def parse_developer_info(soup: BeautifulSoup, chrome_extension: ChromeExtension):
    # NAME
    chrome_extension.developer_name = find_tag_and_get_text(soup, "div", "C2WXF")
    if len(chrome_extension.developer_name) == 0:
        offered_by_li = soup.find("li", class_='ZbWJPd T7iRm')
        if offered_by_li:
            developer_name = ' '.join(offered_by_li.stripped_strings).replace('Offered by', '').strip()
            chrome_extension.developer_name = developer_name
        # else: We can try getting it from the address below

    # ADDRESS
    # <div class="Fm8Cnb">Cloudhiker<br>Sedanstraße 24
    # Berlin 12167
    # DE</div>
    developer_address_div = soup.find('div', class_='Fm8Cnb')
    if developer_address_div:
        full_text = developer_address_div.decode_contents().strip()
        split_pattern = re.compile(r'<br\s*/?>', re.IGNORECASE)
        text_parts = split_pattern.split(full_text)
        print("developer_address_div", full_text, " PARTS: ", text_parts)
        if len(chrome_extension.developer_name) == 0:
            chrome_extension.developer_name = text_parts[0].strip()
        if len(text_parts) > 1:
            address_text = (' '.join(text_parts[1:])).strip()
            # save it as a list of lines
            chrome_extension.developer_address = address_text.split('\n')

    # LINK
    developer_link_a = soup.find("a", "XQ8Hh")
    if not developer_link_a:
        developer_link_a = soup.find("a", "Gztlsc")
    chrome_extension.developer_link = (
        developer_link_a.get("href") if developer_link_a else None
    )

    # EMAIL
    chrome_extension.developer_email = find_tag_and_get_text(soup, "div", "yNyGQd", "AxYQf")

    # try LINK one more time
    # e.g. https://chromewebstore.google.com/detail/quixy-toolbox-free-text-e/dmfjonjeonmaoehpjaonkjgfdjanapbe
    if chrome_extension.developer_link is None:
        if chrome_extension.developer_email:
            email_chunks = chrome_extension.developer_email.split('@')
            chrome_extension.developer_link = email_chunks[1] if len(email_chunks) > 1 else None
    if chrome_extension.developer_link is None:
        # Try to get it from the Privacy Policy field
        privacy_policy_a = soup.find("a", "SYhWge")
        if privacy_policy_a:
            parsed_url = urlparse(privacy_policy_a.get("href"))
            scheme = parsed_url.scheme if parsed_url.scheme else "https"
            chrome_extension.developer_link = standardize_url(f"{scheme}://{parsed_url.netloc}/")

    # try NAME one more time
    if len(chrome_extension.developer_name) == 0:
        if chrome_extension.developer_link:
            # They usually provide some link, so lets just assume the name from it
            parsed_developer_url = urlparse(chrome_extension.developer_link)
            chrome_extension.developer_name = str(parsed_developer_url.netloc)

    # TODO(P2, data): We can access developer_type from the amount of verification it has from Chrome
    # div class HPTfYd-IqDDtd  like "Good record" or "No violations"


# TODO(P0, data): Make sure this works with historical versions of the plugin page
# TODO(P1, reliability): Consume all exceptions and keep on running the job
# TODO(P2, data completeness): There is also /reviews page (defaults to "newest :/" and /support page)
# NOTE: It might happen that `extension_html` is "This item is not available" page
def process_extension_page_response(
    scrape_job: ScrapeChromeExtensionJob, extension_html: str,
):
    soup = BeautifulSoup(extension_html, "html.parser")
    if not is_html_in_english(soup):
        # print(f"WARNING: page is not in English for {scrape_job.url}, rather skipping than getting wrong data.")
        return

    # With "get_or_create" and later .save() we essentially get ON CONFLICT UPDATE (in two statements).
    chrome_extension, created = ChromeExtension.get_or_create(
        google_id=scrape_job.google_id,
        p_date=scrape_job.p_date,
        # marketplace_link might be unknown for plugins which were removed from the store
    )
    chrome_extension: ChromeExtension
    if created:
        print(f"INFO: will CREATE new ChromeExtension entry for {scrape_job.p_date} {scrape_job.google_id}")
    else:
        print(
            f"INFO: will UPDATE existing ChromeExtension entry {scrape_job.p_date} {scrape_job.google_id}"
        )

    # MAIN STUFF
    # Fill in optional scrape job params if they are not provided (MAYBE just better to always get them)
    if scrape_job.name is None:
        name = find_tag_and_get_text(soup, "h1", "Pa2dE", "eFHPDf")
    else:
        name = scrape_job.name

    if scrape_job.marketplace_link is None:
        marketplace_link = get_marketplace_link(soup)
    else:
        marketplace_link = scrape_job.marketplace_link
    chrome_extension.name = name
    chrome_extension.link = marketplace_link
    chrome_extension.source_url = scrape_job.url

    chrome_extension.landing_page_url = find_tag_and_get_text(soup, "a", "cJI8ee")
    chrome_extension.is_featured = soup.find("span", class_="OmOMFc") is not None

    # GOING AS THE PAGE GOES: TOP OF THE PAGE
    img_logo_tag = soup.find("img", class_="rBxtY")
    chrome_extension.logo_link = img_logo_tag.get("src") if img_logo_tag else None
    featured_img_tag = soup.find("img", class_="VuCTZc")
    if not featured_img_tag:
        featured_img_tag = soup.find("img", class_="LAhvXe")
    chrome_extension.featured_img_link = (
        featured_img_tag.get("src") if featured_img_tag else None
    )

    category_and_users_tag = soup.find("div", class_="F9iKBc")
    if category_and_users_tag:
        chrome_extension.categories = [
            category_tag.text for category_tag in category_and_users_tag.find_all("a")
        ]
        # HARD DATA - THE MOST IMPORTANT PART
        chrome_extension.user_count = extract_number_best_effort(
            re.sub("[^0-9]", "", category_and_users_tag.text)
        )
    else:
        print(f"WARNING: cannot find category and user count for {scrape_job.url}")

    # e.g. 11.7K ratings
    rating_count_str = find_tag_and_get_text(soup, "p", "xJEoWe")
    chrome_extension.rating_count = extract_number_best_effort(rating_count_str)
    if chrome_extension.rating_count == 0:
        # They actually say that rating = 5 if there are no ratings, but we will just leave it as None
        chrome_extension.rating = None
    else:
        chrome_extension.rating = find_tag_and_get_text(soup, "span", "Vq0ZA")

    # TODO(P2, verify): This seems to be hidden on the details page, but they using the same class name
    #   as on the listing page so might just work!
    chrome_extension.description = find_tag_and_get_text(soup, "p", "Uufqmb")
    if should_save_large_fields(scrape_job.p_date):
        overview_div = soup.find("div", class_="uORbKe")
        if overview_div:
            chrome_extension.overview = "\n".join(
                [p_tag.text for p_tag in overview_div.find_all("p")]
            )

    chrome_extension.released_version = find_tag_and_get_text(soup, "div", "pDlpAd", "N3EXSc")

    parse_listing_updated(soup, chrome_extension)
    parse_developer_info(soup, chrome_extension)

    # This can be Empty, maybe we should set it NONE
    # E.g. "The developer has disclosed that it will not collect or use your data"
    if should_save_large_fields(scrape_job.p_date):
        chrome_extension.permissions = [
            span_tag.text for span_tag in soup.find_all("span", "PuNHYb")
        ]
        if len(chrome_extension.permissions) == 0:
            chrome_extension.permissions = [
                span_tag.text for span_tag in soup.find_all("span", "jnapE")
            ]

    # NOTE: yes this could benefit from asyncio,
    # but DB calls are usually way faster (3-10ms) than the HTTP GET (100-1000ms) to get here so it is fine.
    chrome_extension.save()
    # TODO(P2, feature): Review text from chrome_extension.link + "/reviews (unfortunately it defaults to "newest" :/)


# looks like bmnlcjabgnpnenekpadlanbbkooimhnj
def get_extension_id_from_link(link: str) -> str:
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


async def scrape_chrome_extensions_in_parallel(scrape_jobs: List[ScrapeChromeExtensionJob], rescrape_existing=False):
    print("Gonna scrape_chrome_extensions_in_parallel for ", len(scrape_jobs), " extensions")
    tasks = []
    semaphore = asyncio.Semaphore(ASYNC_IO_MAX_PARALLELISM)

    for scrape_job in scrape_jobs:
        # if ChromeExtension.exists(scrape_job.google_id, scrape_job.p_date) and not rescrape_existing:
        #     print(f"INFO: skipping already scraped extension {scrape_job.google_id} {scrape_job.p_date}")
        #     continue

        # Schedule the task with semaphore
        task = async_research_extension_more(scrape_job, semaphore)
        tasks.append(asyncio.create_task(task))
        # sync_research_extension_more(chrome_extension)

    if len(tasks) > 0:
        print(
            f"INFO: Main 'thread' waiting on all {len(tasks)} asyncio tasks START"
        )
        await asyncio.gather(*tasks)


async def get_all_chrome_extensions_from_marketplace(p_date: str) -> List[ScrapeChromeExtensionJob]:
    researched_extensions = set()
    scrape_jobs = []
    print(
        f"will run individual app HTTP GET with {ASYNC_IO_MAX_PARALLELISM} max parallelism"
    )

    # TODO(P1, runtime): Ideally this would be a generator so we can start scraping while parsing listing pages
    for listing_page in LISTS:
        get_extensions_from_listing_page(listing_page, p_date=p_date)
        for scrape_job in scrape_jobs:
            # Already visited? In-memory version
            link = scrape_job.marketplace_link
            if link in researched_extensions:
                print(f"INFO: skipping already researched extension {scrape_job.marketplace_link}")
                continue
            scrape_jobs.append(scrape_job)
            researched_extensions.add(link)

    return scrape_jobs


def get_scrape_job_for_google_id(google_id, p_date):
    return ScrapeChromeExtensionJob(
        url=f"https://chromewebstore.google.com/detail/HELLO-WORLD-HAHAHA/{google_id}",
        p_date=p_date,
        google_id=google_id,
    )


def get_all_chrome_extensions_from_database(p_date: str) -> List[ScrapeChromeExtensionJob]:
    # For Chrome Extensions we only need the google_id to scrape it with the HAHAHA Hack
    distinct_google_ids = (ChromeExtension
                           .select(ChromeExtension.google_id)
                           .distinct())

    # Execute the query and fetch the results
    result = []
    for entry in distinct_google_ids:
        result.append(get_scrape_job_for_google_id(entry.google_id, p_date))
    return result


if __name__ == "__main__":
    # We will ignore the complexity of timezones
    batch_job_p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        asyncio.run(get_all_chrome_extensions_from_marketplace(batch_job_p_date))
