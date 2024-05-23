import asyncio
import json
import os
import random
import re
import string
from datetime import datetime
from glob import glob
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from supawee.client import connect_to_postgres

from batch_jobs.backfill.backfill_scrape import backfill_chrome_extension_with_wayback
from batch_jobs.common import extract_number_best_effort, standardize_url
from batch_jobs.scraper.chrome_extensions import get_scrape_job_for_google_id, scrape_chrome_extensions_in_parallel
from common.config import POSTGRES_DATABASE_URL
from supabase.models.data import ChromeExtension


# TODO(P0, data): For historical Chrome Extension user/rating data use this repo as Wayback Machine will take forever:
#   100,000 Chrome Extensions, up to once a month, 4 years back, say 10 historical datapoints on average
#   1,000,000 Wayback Machine requests, with 5-15 requests per minute, 1,000 to 3,000 hours runtime (50-150 days).
# TODO: Also add released_date and other stuff while doing it
# https://github.com/palant/chrome-extension-manifests-dataset?tab=readme-ov-file
# They have 8 historical datapoints, which is nice:
# manifests-2021-10-30/ manifests-2022-09-08/ manifests-2023-05-08/ manifests-2023-06-05/ manifests-2023-11-17/ manifests-2024-01-12/  # noqa
# manifests-2022-08-08/ manifests-2023-03-15/ manifests-2023-06-01/ manifests-2023-09-21/ manifests-2023-11-29/ manifests-2024-04-13/  # noqa
# cat manifests-2024-04-13/aaaaahnmcjcoomdncaekjkjedgagpnln.json
# ---
# name: Contextual Search for YouTube
# version: 1.0.0.14
# category_slug: productivity/tools
# rating: 4.769230769230769
# rating_count: 13
# user_count: 908
# release_date: '2022-07-31T10:26:25.000Z'
# size: 13.0KiB
# languages:
#   - English
# description: >-
#   Allows the user search YouTube for a term by highlighting text and selecting
#   'Search YouTube for...' from the right click menu.
# publisher_account: Gryff
# ---
#
# {
#   "update_url": "https://clients2.google.com/service/update2/crx",
#   "manifest_version": 3,
#   "name": "Contextual Search for YouTube",
#   "background": {
#     "service_worker": "searchyoutube.js"
#   },
#   "description": "Allows the user search YouTube for a term by highlighting text and selecting 'Search YouTube for...' from the right click menu.",
#   "icons": {
#     "16": "SmallIcon.png",
#     "48": "MediumIcon.png"
#   },
#   "version": "1.0.0.14",
#   "permissions": [
#     "contextMenus"
#   ]
# }


def remove_single_line_comments(json_str):
    # Regex to remove single-line comments that start with // but are not inside quotes
    pattern = r'(^|\s)//.*?$'
    in_string = False
    clean_lines = []

    for line in json_str.splitlines():
        # Toggle the in_string flag when encountering unescaped quotes
        for i, char in enumerate(line):
            if char == '"' and (i == 0 or line[i - 1] != '\\'):
                in_string = not in_string

        # If not inside a string, remove the comment
        if not in_string:
            line = re.sub(pattern, '', line, flags=re.MULTILINE)

        clean_lines.append(line)

    return '\n'.join(clean_lines)


def parse_manifest_file(file_path: str, encoding: str='utf-8') -> Dict[str, Any]:
    # Attempt to read the file with standard UTF-8 encoding
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()

    # Split the content into YAML and JSON parts
    parts = content.split('---\n')

    # Parse YAML and JSON sections
    yaml_part = str(parts[1]).strip()
    yaml_data = yaml.safe_load(yaml_part) if len(yaml_part) > 0 else dict()
    json_part = remove_single_line_comments(str(parts[2]).strip())
    try:
        json_data = json.loads(json_part) if len(json_part) > 0 else dict()
    except json.JSONDecodeError as e:
        if "Unexpected UTF-8 BOM" in str(e):
            if encoding != "utf-8-sig":
                print(f"Retrying with utf-8-sig encoding for {file_path}")
                return parse_manifest_file(file_path, encoding="utf-8-sig")
            json_data = {}
            print(f"Error while parsing JSON in {file_path}: {e}")
        else:
            raise e

    # Merge the two dictionaries
    data = {**yaml_data, **json_data}

    for key in ['rating', 'rating_count', 'user_count']:
        if key in data:
            data[key] = extract_number_best_effort(str(data[key]))

    for key in ['publisher_site', 'extension_website', 'support_website', 'updated_url', 'homepage_url']:
        if key in data:
            data[key] = standardize_url(data[key])

    return data


def backfil_chrome_extension_manifests_dataset(base_path: str = "/Users/petercsiba/code/chrome-extension-manifests-dataset"):
    all_keys = set()

    for dir_path in glob(os.path.join(base_path, 'manifests-*')):
        p_date = os.path.basename(dir_path).split('-', maxsplit=1)[1]
        print(f"Processing p_date={p_date} from {dir_path}")
        if p_date in ["2021-10-30"]:
            continue

        filepaths = glob(os.path.join(dir_path, '*.json'))
        for i, file_path in enumerate(filepaths):
            if (i + 1) % 100 == 0:
                print(f"Processing file {i}/{len(filepaths)}")

            google_id = os.path.basename(file_path).split('.')[0]

            try:
                content = parse_manifest_file(file_path)
            except Exception as e:
                print(f"Error while parsing {file_path}: {e}")
                raise e

            all_keys.update(content.keys())
            # Insert data into the Peewee model
            extension, created = ChromeExtension.get_or_create(
                google_id=google_id,
                p_date=p_date,
            )
            if not created:
                continue

            extension: ChromeExtension
            # Update fields only if the new values are present in the content
            extension.name = content.get('name', extension.name)
            extension.released_version = content.get('version', extension.released_version)
            extension.category_slug = content.get('category_slug', extension.categories)
            extension.rating = content.get('rating', extension.rating)
            extension.rating_count = content.get('rating_count', extension.rating_count)
            extension.user_count = content.get('user_count', extension.user_count)
            extension.description = content.get('description', extension.description)
            extension.developer_address = content.get('publisher_address', extension.developer_address)
            extension.developer_link = content.get('publisher_site', extension.developer_link)

            if extension.landing_page_url is None:
                extension.landing_page_url = content.get('extension_website')
            if extension.landing_page_url is None:
                extension.landing_page_url = content.get('homepage_url')

            extension.developer_name = content.get('publisher_account', extension.developer_name)
            if 'permissions' in content:
                permissions = content.get('permissions')
                if isinstance(permissions, dict):
                    permissions = permissions.values()
                extension.permissions = ','.join(permissions)
            extension.source_url = "https://github.com/palant/chrome-extension-manifests-dataset" + file_path

            extension.save()

    print("All keys:", all_keys)


# For Chrome Extensions
async def backfill_chrome_extensions_list():
    batch_job_p_date = datetime.today().strftime("%Y-%m-%d")

    with open("batch_jobs/backfill/data/chrome-extensions-google-id-full.txt", "r") as f:
        google_id_list = f.read().splitlines()

    # NOTE: The slug part is only for SEO, you can put anything there
    scrape_jobs = []
    for google_id in google_id_list:
        scrape_jobs.append(get_scrape_job_for_google_id(google_id, batch_job_p_date))

    scrape_jobs.reverse()   # Just that I already did the first N
    await scrape_chrome_extensions_in_parallel(scrape_jobs, rescrape_existing=False)


def generate_random_shard_prefix() -> str:
    letters = string.ascii_lowercase[:16]  # 'a' to 'p'
    return ''.join(random.choice(letters) for _ in range(2))


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


if __name__ == "__main__":
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        backfil_chrome_extension_manifests_dataset()
        # asyncio.run(backfill_chrome_extensions_list())
        # shard_prefix = generate_random_shard_prefix()
        # backfill_chrome_extension_with_wayback(shard_prefix=shard_prefix)
