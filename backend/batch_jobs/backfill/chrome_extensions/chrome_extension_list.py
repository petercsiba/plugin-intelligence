import asyncio
import random
import string
from datetime import datetime

from supawee.client import connect_to_postgres

from batch_jobs.backfill.backfill_scrape import backfill_chrome_extension_with_wayback
from batch_jobs.scraper.chrome_extensions import get_scrape_job_for_google_id, scrape_chrome_extensions_in_parallel
from common.config import POSTGRES_DATABASE_URL


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


if __name__ == "__main__":
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        # asyncio.run(backfill_chrome_extensions_list())
        shard_prefix = generate_random_shard_prefix()
        backfill_chrome_extension_with_wayback(shard_prefix=shard_prefix)
