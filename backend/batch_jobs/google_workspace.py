# TODO(P1, feature:trends): Can get historical data through WayBack
#  curl "http://archive.org/wayback/available?url=<LINK>&timestamp=20240101" | jq .
#  https://web.archive.org/web/20231101062549/https://workspace.google.com/marketplace/app/mail_merge/218858140171
import csv
import re
import urllib
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from typing import Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup, Tag
from supawee.client import connect_to_postgres

from config import POSTGRES_DATABASE_URL
from supabase.models.data import GoogleAddOn

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

# TODO(P1, completeness): Some might be missing, and https://workspace.google.com/marketplace/sitemap.xml isn't enough
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


@dataclass
class AppData:
    name: str
    developer: str
    rating: str
    rating_count: int
    users: int
    link: str
    listing_updated: str = field(default="")
    description: str = field(default="")
    pricing: str = field(default="")
    with_drive: bool = field(default=False)
    with_docs: bool = field(default=False)
    with_sheets: bool = field(default=False)
    with_slides: bool = field(default=False)
    with_forms: bool = field(default=False)
    with_calendar: bool = field(default=False)
    with_gmail: bool = field(default=False)
    with_meet: bool = field(default=False)
    with_classroom: bool = field(default=False)
    with_chat: bool = field(default=False)
    developer_link: str = field(default="")
    overview: str = field(default="")
    permissions: list = field(default_factory=list)
    reviews: list = field(default_factory=list)

    # Takes in subset of
    # ['Google Drive', 'Google Docs', 'Google Sheets', 'Google Slides', 'Google Forms', 'Google Calendar',
    #  'Gmail', 'Google Meet', 'Google Classroom', 'Google Chat']
    def fill_in_works_with(self, works_with: list):
        self.with_drive = "Google Drive" in works_with
        self.with_docs = "Google Docs" in works_with
        self.with_sheets = "Google Sheets" in works_with
        self.with_slides = "Google Slides" in works_with
        self.with_forms = "Google Forms" in works_with
        self.with_calendar = "Google Calendar" in works_with
        self.with_gmail = "Gmail" in works_with
        self.with_meet = "Google Meet" in works_with
        self.with_classroom = "Google Classroom" in works_with
        self.with_chat = "Google Chat" in works_with

    # For debugging purposes
    def display(self):
        print("--- App Data ---")
        print(f"Name: {self.name}")
        print(f"Developer: {self.developer}")
        print(f"Rating: {self.rating} out of {self.rating_count} reviews")
        print(f"Users: {self.users}")
        print(f"Link: {self.link}")
        print(f"Listing Updated: {self.listing_updated}")
        print(f"Description: {self.description}")
        print(f"Pricing: {self.pricing}")
        # print(f'Works With: {", ".join(self.works_with)}')
        print(f"Developer Link: {self.developer_link}")
        print(f'Permissions: {", ".join(self.permissions)}')
        reviews_str = "\n".join([str(r) for r in self.reviews])
        print(f"Most Relevant Reviews: {reviews_str}")


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


def get_apps(url: str):
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
        user_span = app.find("span", class_="kVdtk").find_next_sibling("span")
        if user_span is not None:
            users = parse_user_count(user_span.text.strip())
        else:
            users = None

        # Fill in the data available from the listings table page, more will be filled from individual pages.
        app_data = AppData(
            name=find_tag_and_get_text(app, "div", "M0atNd"),
            developer=find_tag_and_get_text(app, "span", "y51Cnd"),
            rating=find_tag_and_get_text(app, "span", "wUhZA"),
            rating_count=0,  # will be updated
            users=users,
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


def parse_permissions(soup):
    permission_elements = soup.find_all("span", class_="jyBTLc")
    return [element.text.strip() for element in permission_elements]


def parse_reviews(soup):
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


def research_app_more(app_data: AppData):
    print(f"getting more app_data for {app_data.name} from {app_data.link}")

    response = requests.get(app_data.link)
    if response.status_code != 200:
        print("could not get data")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    rating_count_el = soup.find("span", itemprop="ratingCount")
    app_data.rating_count = rating_count_el.text.strip() if rating_count_el else None
    app_data.listing_updated = find_tag_and_get_text(soup, "div", "bVxKXd").replace(
        "Listing updated:", ""
    )
    app_data.description = find_tag_and_get_text(soup, "div", "kmwdk")
    app_data.pricing = find_tag_and_get_text(soup, "span", "P0vMD")
    # app_data.works_with = get_works_with(app=soup)
    app_data.fill_in_works_with(get_works_with_list(soup=soup))
    # TODO: gpt to summarize - probably in another script
    app_data.overview = find_tag_and_get_text(soup, "pre", "nGA4ed")
    app_data.developer_link = get_developer_link(soup=soup)
    # TODO (this needs some clicking)
    app_data.permissions = parse_permissions(soup=soup)
    app_data.reviews = parse_reviews(soup=soup)
    # app_data.display()


def get_google_id_from_link(link: str):
    parsed_url = urllib.parse.urlparse(link)
    return parsed_url.path.split("/")[-1]


def main():
    fieldnames = [
        f.name for f in fields(AppData)
    ]  # Dynamically get the field names from the dataclass

    now = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")

    with connect_to_postgres(POSTGRES_DATABASE_URL):
        with open(f"batch_jobs/data/output-{now}.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            researched_apps = set()

            for listing_page in LISTS:
                apps = get_apps(listing_page)
                for app_data in apps:
                    link = app_data.link
                    if link in researched_apps:
                        continue
                    researched_apps.add(link)

                    add_on = GoogleAddOn()
                    add_on.google_id = get_google_id_from_link(link)
                    add_on.p_date = p_date
                    add_on.name = app_data.name
                    add_on.link = app_data.link
                    add_on.save()

                    research_app_more(app_data)
                    app_data_dict = asdict(app_data)
                    writer.writerow(app_data_dict)

                    break


if __name__ == "__main__":
    main()
