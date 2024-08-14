import asyncio
import os
import time
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from peewee import fn
from supawee.client import connect_to_postgres

from batch_jobs.scraper.chrome_extensions import ScrapeChromeExtensionJob, process_extension_page_response
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
from supabase.models.base import BaseGoogleWorkspace, BaseChromeExtension
from supabase.models.data import GoogleWorkspace, ChromeExtension

MIN_BATCH = 100
# TODO(P1, completenesse): Did first run with day_steps=1, BUT unsure if there is too much value in that
#   this really only affects the most popular ones
WAYBACK_DAY_STEPS = 90


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
    # Subquery to find google_id with MIN(p_date) - so we skip those already scraped from Wayback
    subquery = (
        BaseGoogleWorkspace
        .select(BaseGoogleWorkspace.google_id)
        .group_by(BaseGoogleWorkspace.google_id)
        .having(fn.MIN(BaseGoogleWorkspace.p_date) > '2024-04-01')
    )

    # Main query selecting distinct links with user_count and applying the subquery
    distinct_links = (
        BaseGoogleWorkspace
        .select(BaseGoogleWorkspace.link, BaseGoogleWorkspace.user_count)
        .distinct()
        .where(
            BaseGoogleWorkspace.link.is_null(False) &
            BaseGoogleWorkspace.user_count.is_null(False) &
            (BaseGoogleWorkspace.google_id.in_(subquery))
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
                wayback_get_all_snapshot_urls(target_url=target_url, day_step=WAYBACK_DAY_STEPS)
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


def backfill_chrome_extension_with_wayback():
    print("Getting distinct chrome extension links which we didn't scrape with Wayback yet ...")

    # Subquery to filter out google_ids with any source_url containing 'wayback'
    exclusion_subquery = (
        BaseChromeExtension
        .select(BaseChromeExtension.google_id)
        .where(BaseChromeExtension.source_url.contains('web.archive.org'))
        .distinct()
    )

    # Subquery to get the most recent link for each google_id
    subquery = (
        BaseChromeExtension
        .select(
            BaseChromeExtension.google_id,
            fn.MAX(BaseChromeExtension.p_date).alias('max_p_date')
        )
        .where(
            BaseChromeExtension.google_id.not_in(exclusion_subquery)
        )
        .group_by(BaseChromeExtension.google_id)
    )

    # Main query to join with the subquery and get the required fields
    distinct_links_query = (
        BaseChromeExtension
        .select(
            BaseChromeExtension.link,
            BaseChromeExtension.google_id,
            BaseChromeExtension.user_count
        )
        .join(
            subquery,
            on=(
                    (BaseChromeExtension.google_id == subquery.c.google_id) &
                    (BaseChromeExtension.p_date == subquery.c.max_p_date)
            )
        )
        .where(BaseChromeExtension.link.is_null(False))
        .order_by(fn.COALESCE(BaseChromeExtension.user_count, 0).desc())
    )

    # Execute the query
    distinct_links = distinct_links_query.execute()

    print("Distinct links count:", len(distinct_links))

    total_scraped = 0
    scraping_start = time.time()
    for partial_chrome_extension in distinct_links:
        marketplace_link = partial_chrome_extension.link
        wayback_snapshots = wayback_get_all_snapshot_urls(target_url=marketplace_link, day_step=WAYBACK_DAY_STEPS)

        scrape_jobs = []
        for snapshot in wayback_snapshots:
            scrape_jobs.append(
                ScrapeChromeExtensionJob(
                    url=snapshot.wayback_url(),
                    p_date=snapshot.p_date_str(),
                    marketplace_link=marketplace_link,
                    google_id=partial_chrome_extension.google_id,
                )
            )

        # TODO(P3, devx): This is duplicate code from backfill_google_workspace, at some point we will abstract this
        print(f"Accumulated enough jobs {len(scrape_jobs)}, gonna scrape one-by-one...")
        for scrape_job in scrape_jobs:
            if ChromeExtension.exists(scrape_job.google_id, scrape_job.p_date):
                print(f"Skipping as it is already scraped: {scrape_job.url}")
                continue

            print(
                f"Scraping ({scrape_job.google_id}, {scrape_job.p_date}) from ",
                scrape_job.url,
            )
            response = requests_get_with_retry(scrape_job.url)
            if response and response.status_code == 200:
                process_extension_page_response(scrape_job, response.text)
                total_scraped += 1
            else:
                print(f"WARNING: cannot get contents of {scrape_job.url}")

        avg_per_minute = 60 * total_scraped / (time.time() - scraping_start)
        print(f"Total scraped so far: {total_scraped}; on average {avg_per_minute} per minute")


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


if __name__ == "__main__":
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        # backfill_google_workspace()
        backfill_chrome_extension_with_wayback()
