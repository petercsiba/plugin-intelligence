import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, urlunparse

from bs4 import Tag, BeautifulSoup

# How many concurrent HTTP GET can run in the scraper. The ideal here depends on the provisioned machine,
# and how the scraper target domain is sensitive. This is a super-basic scraper, but if it ain't working
# might make sense to use a library / service.
ASYNC_IO_MAX_PARALLELISM = 1


# We return empty string for convenience so we can chain with .replace() or .strip() without checking for None
def find_tag_and_get_text(element: Tag, tag_name: str, class_name: str) -> str:
    found_element = element.find(tag_name, class_=class_name)
    return found_element.text.strip() if found_element else ""


# extract_number_best_effort finds first number-like string and returns it as a float (usually it is int).
# Example usage
# text1 = "Average rating: 3.62 out of 5. 258 users rated this item."
# text2 = "The company earned 2.5M dollars last year."
# text3 = "This video has 12K views."
#
# print(extract_first_number(text1))  # Output: 3.62
# print(extract_first_number(text2))  # Output: 2500000.0
# print(extract_first_number(text3))  # Output: 12000.0
def extract_number_best_effort(int_str: Optional[str]) -> float:
    if int_str == "" or int_str is None:
        return 0

    int_str = int_str.replace(",", "")
    # Find numbers with optional K or M suffix
    match = re.search(r'(\d+\.?\d*)([KM]?)', int_str)
    if not match:
        return 0

    number = float(match.group(1))
    multiplier = {"K": 1000, "M": 1000000}
    suffix = match.group(2)
    if suffix in multiplier:
        number *= multiplier[suffix]
    return number


def listing_updated_str_to_date(listing_updated_str: str) -> datetime.date:
    try:
        # "April 24, 2024"
        return datetime.strptime(listing_updated_str, "%B %d, %Y").date()
    except ValueError as e:
        if len(listing_updated_str) > 2:
            print(
                f"info: cannot parse listing updated for {listing_updated_str} cause: {e}"
            )
        return None


def is_html_in_english(soup: BeautifulSoup) -> bool:
    # Check the lang attribute in the <html> tag
    html_tag = soup.find('html')
    if html_tag and html_tag.has_attr('lang'):
        if 'en' in html_tag['lang'].lower():
            return True

    # Check the lang attribute in <meta> tags
    meta_tags = soup.find_all('meta')
    for meta_tag in meta_tags:
        if meta_tag.get('http-equiv') == 'Content-Language':
            if 'en' in meta_tag.get('content', '').lower():
                return True
        if meta_tag.get('name') == 'language':
            if 'en' in meta_tag.get('content', '').lower():
                return True

    # Optionally, check text content for further validation (if necessary)
    # This part can be expanded with more sophisticated language detection if needed
    return False


def standardize_url(url: str) -> Optional[str]:
    try:
        # Ensure the URL has a scheme
        if not urlparse(url).scheme:
            url = 'http://' + url

        # Parse the URL
        parsed_url = urlparse(url)

        # Check if the scheme and netloc are present
        if not parsed_url.scheme or not parsed_url.netloc or len(parsed_url.scheme) == 0:
            return None
        print("scheme: ", parsed_url.scheme)

        # Ensure netloc does not contain invalid characters like "://"
        if '://' in parsed_url.netloc or not parsed_url.netloc:
            return None

        # Upgrade http to https, keep other schemes as is
        scheme = 'https' if parsed_url.scheme in ['http', 'https'] else parsed_url.scheme

        # Add www if missing
        netloc = parsed_url.netloc.lower()
        if len(netloc.split(".")) <= 2:
            netloc = 'www.' + netloc

        # Remove default port 80 if present
        if netloc.endswith(':80'):
            netloc = netloc[:-3]

        # Standardize the rest of the URL components
        path = parsed_url.path if parsed_url.path else '/'
        params = parsed_url.params
        query = parsed_url.query
        fragment = parsed_url.fragment

        # Rebuild the URL
        standardized_url = urlunparse((scheme, netloc, path, params, query, fragment)).lower()
        return standardized_url
    except Exception as e:
        # Return None if any error occurs
        print(f"Error standardizing URL {url}: ", e)
        return None
