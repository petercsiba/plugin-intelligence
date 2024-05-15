import re
from slugify import slugify


def slugify_company_name(name: str) -> str:
    return slugify(standardize_company_name(name))


# TODO: Double-check this is idempotent, i.e. we can call it indefinitely and yields the same result
def standardize_company_name(name: str) -> str:
    # List of common suffixes and terms to remove
    suffixes = [
        "Inc", "LLC", "Ltd", "Pvt", "Corporation", "Corp", "Incorporated", "Limited",
        "Company", "Co", "SIA", "AG", "GmbH", "BV", "NV", "PLC", "LP", "LLP", "PC",
        "PLLC", "PT", "Tbk", "SpA", "SA", "SL", "OY", "AB", "AS", "A/S", "株式会社",
        "有限会社", "有限公司", "주식회사"
    ]

    # Remove suffixes
    name = re.sub(r'\b(?:' + '|'.join(suffixes) + r')\b', '', name, flags=re.IGNORECASE | re.UNICODE)
    print(name)

    chunks = name.split()
    if len(chunks) > 1:
        # Sometimes they include the domain name into the company name, so we need to remove it
        # BUT only if it is redundant.
        last_chunk = chunks[-1]
        print("last_chunk", last_chunk)
        # Pattern to match web addresses (URLs); God Bless ChatGPT
        pattern = r'\b(?:http[s]?://|www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?\b'
        last_chunk = re.sub(pattern, '', last_chunk)
        print("last_chunk", last_chunk)
        chunks[-1] = last_chunk

    # Ensure capitalization
    name = ' '.join(word.capitalize() for word in chunks)
    print(name)

    # Remove non-alphanumeric characters at beginning and end
    name = re.sub(r'^[^\w]+|[^\w]+$', '', name, flags=re.UNICODE)
    print(name)

    # Remove punctuation around suffixes and other extraneous punctuation
    name = re.sub(r'[\|,.]', '', name)
    print(name)

    return name
