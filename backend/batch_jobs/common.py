import re
from datetime import datetime

from bs4 import Tag

# How many concurrent HTTP GET can run in the scraper. The ideal here depends on the provisioned machine,
# and how the scraper target domain is sensitive. This is a super-basic scraper, but if it ain't working
# might make sense to use a library / service.
ASYNC_IO_MAX_PARALLELISM = 6


def find_tag_and_get_text(element: Tag, tag_name: str, class_name: str) -> str:
    found_element = element.find(tag_name, class_=class_name)
    return found_element.text.strip() if found_element else ""


# parse_user_count converts strings like '4K' to '4000' and '1M' to '1000000'
def parse_shortened_int_k_m(int_str: str) -> int:
    if int_str == "":
        return 0

    multiplier = {"K": 1000, "M": 1000000}
    match = re.search(r"(\d+)([KM])", int_str)
    if match:
        number = int(match.group(1))
        suffix = match.group(2)
        return number * multiplier[suffix]

    try:
        return int(int_str)
    except ValueError as e:
        print(f"WARNING: cannot parse_shortened_int_k_m for '{int_str}' cause: {e}")
        return 0


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
