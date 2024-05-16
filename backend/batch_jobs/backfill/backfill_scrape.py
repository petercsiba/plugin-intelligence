import asyncio
import os
import time
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from supawee.client import connect_to_postgres

from batch_jobs.scraper.chrome_extensions import ScrapeChromeExtensionJob, scrape_chrome_extensions_in_parallel
from batch_jobs.scraper.google_workspace import (
    ScrapeAddOnDetailsJob,
    scrape_google_workspace_add_ons,
    get_google_id_from_marketplace_link,
    sync_scrape_add_on_details,
    process_add_on_page_response,
)
from batch_jobs.scraper.wayback import (
    wayback_get_all_snapshot_urls,
    requests_get_with_retry,
)
from common.config import POSTGRES_DATABASE_URL
from supabase.models.base import BaseGoogleWorkspace
from supabase.models.data import GoogleWorkspace

MIN_BATCH = 100


def google_workspace_previous_domains() -> List[str]:
    # God bless Wikipedia and Web Archive: https://en.wikipedia.org/wiki/Google_Workspace_Marketplace
    # End googleblog https://workspaceupdates.googleblog.com/2010/03/google-apps-marketplace-now-launched.html
    return [
        # From about 20201013190250 til now
        "workspace.google.com",
        # From about 20170512003629:
        # https://web.archive.org/web/20170512003629id_/https://gsuite.google.com/marketplace
        # BUT they changed the ID format around 2020 - and it's hard to get those :/
        # e.g. https://gsuite.google.com/marketplace/app/pipdgoflicmpcfocpejndfeegjmeokfh -> 466680526474
        # IN THEORY we can get this by scraping the old marketplace listing pages (not the javascript ones)
        # and then Google now redirects old IDs to new ones, so we can get the new ID from the redirect.
        "gsuite.google.com",
        # From about 20151015160059:
        # https://web.archive.org/web/20151015160059id_/https://apps.google.com/marketplace/
        # "apps.google.com", TODO(P2, historical): One day someone really really asks for it
        # before more complicated seems up until 20080414195237:
        # https://web.archive.org/web/20080414195237id_/http://www.google.com:80/enterprise/marketplace/home
        # e.g. https://web.archive.org/web/20100415090845id_/http://www.google.com/enterprise/marketplace/viewListing?productListingId=2533+17854168373705313802&hp=featured  # noqa
        # which is now https://workspace.google.com/marketplace/app/zoho_crm/469571659015
    ]


# Estimated time:
# * About 3,000 apps in the marketplace
# * Lets say 5-10 historical links for each
# * 15,000-30,000 requests with 5-15 requests per minute
# * 1,000-6,000 minutes = 16-100 hours runtime
def backfill_google_workspace():
    distinct_links = (
        BaseGoogleWorkspace.select(
            BaseGoogleWorkspace.link, BaseGoogleWorkspace.user_count
        )
        .distinct()
        .where(
            BaseGoogleWorkspace.link.is_null(False)
            & BaseGoogleWorkspace.user_count.is_null(False)
        )
        .order_by(BaseGoogleWorkspace.user_count.desc())
    )
    print("Distinct links count:", distinct_links.count())

    total_scraped = 0
    scraping_start = time.time()
    for add_on in distinct_links:
        wayback_snapshots = []
        for previous_domain in google_workspace_previous_domains():
            target_url = add_on.link.replace("workspace.google.com", previous_domain)
            wayback_snapshots.extend(
                wayback_get_all_snapshot_urls(target_url=target_url, day_step=1)
            )

        scrape_jobs = []
        for snapshot in wayback_snapshots:
            scrape_jobs.append(
                ScrapeAddOnDetailsJob(
                    url=snapshot.wayback_url(),
                    p_date=snapshot.p_date_str(),
                    marketplace_link=add_on.link,
                    google_id=get_google_id_from_marketplace_link(add_on.link),
                )
            )

        print(f"Accumulated enough jobs {len(scrape_jobs)}, gonna scrape one-by-one...")
        for scrape_job in scrape_jobs:
            if GoogleWorkspace.exists(scrape_job.google_id, scrape_job.p_date):
                print(f"Skipping as it is already scraped: {scrape_job.url}")
                continue

            print(
                f"Scraping ({scrape_job.google_id}, {scrape_job.p_date}) from ",
                scrape_job.url,
            )
            response = requests_get_with_retry(scrape_job.url)
            if response and response.status_code == 200:
                process_add_on_page_response(scrape_job, response.text)
                total_scraped += 1
            else:
                print(f"WARNING: cannot get contents of {scrape_job.url}")

        avg_per_minute = 60 * total_scraped / (time.time() - scraping_start)
        print(
            f"Total scraped so far: {total_scraped}; on average {avg_per_minute} per minute"
        )

# TODO(P0, data): For historical Chrome Extension user/rating data use this repo as Wayback Machine will take forever:
#   100,000 Chrome Extensions, up to once a month, 4 years back, say 10 historical datapoints on average
#   1,000,000 Wayback Machine requests, with 5-15 requests per minute, 1,000 to 3,000 hours runtime (50-150 days).
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
        scrape_job = ScrapeChromeExtensionJob(
            url=f"https://chromewebstore.google.com/detail/HELLO-WORLD-HAHAHA/{google_id}",
            p_date=batch_job_p_date,
            google_id=google_id,
        )
        scrape_jobs.append(scrape_job)

    scrape_jobs.reverse()   # Just that I already did the first N
    await scrape_chrome_extensions_in_parallel(scrape_jobs, rescrape_existing=False)


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


if __name__ == "__main__":
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        asyncio.run(backfill_chrome_extensions_list())
        # backfill_google_workspace()
