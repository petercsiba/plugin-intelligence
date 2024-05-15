import re
from slugify import slugify


def slugify_company_name(name: str) -> str:
    return slugify(standardize_company_name(name))


# TODO: Double-check this is idempotent, i.e. we can call it indefinitely and yields the same result
def standardize_company_name(name: str) -> str:
    # List of common suffixes and terms to remove
    suffixes = [
        "Inc",
        "LLC",
        "Ltd",
        "Pvt",
        "Corporation",
        "Corp",
        "Incorporated",
        "Limited",
        "Company",
        "Co",
        "SIA",
        "AG",
        "GmbH",
        "BV",
        "NV",
        "PLC",
        "LP",
        "LLP",
        "PC",
        "PLLC",
        "PT",
        "Tbk",
        "SpA",
        "SA",
        "SL",
        "S.L",
        "OY",
        "AB",
        "AS",
        "A/S",
        "株式会社",
        "有限会社",
        "有限公司",
        "주식회사",
    ]

    # Remove suffixes and any punctuation following them
    name = re.sub(
        r"\b(?:" + "|".join(suffixes) + r")[\.,\s]*\b",
        "",
        name,
        flags=re.IGNORECASE | re.UNICODE,
    )

    maybe_website_chunks = name.split()
    if len(maybe_website_chunks) > 1:
        # Sometimes they include the domain name into the company name, so we need to remove it
        # BUT only if it is redundant.
        last_chunk = maybe_website_chunks[-1]
        # Pattern to match web addresses (URLs); God Bless ChatGPT
        pattern = (
            r"\b(?:http[s]?://|www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?\b"
        )
        maybe_website_chunks[-1] = re.sub(pattern, "", last_chunk)
        name = " ".join(maybe_website_chunks)
        print(name)

    if "." in name:
        # If the name contains a period, it's likely a website-only name
        if name.startswith("www."):
            name = name[4:]  # Remove 'www.'
        if name.count(".") == 1:
            # Capitalize only the domain name part, e.g. google.com -> Google.com
            name = name.capitalize()
        # Leave more complex website names as is e.g. nsspot.herokuapp.com/coincreator
    print(name)

    # Remove non-alphanumeric characters at beginning and end
    name = re.sub(r"^[^\w]+|[^\w]+$", "", name, flags=re.UNICODE)
    print(name)

    # Remove punctuation (we keep "." for website-only names)
    name = re.sub(r"[\|,]", "", name)
    print(name)

    if "." not in name:
        # Ensure capitalization for each word if not a website-only name
        name = " ".join(word.capitalize() for word in name.split())
    print(name)

    return name
