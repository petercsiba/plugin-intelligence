import asyncio
import time
from typing import List

from supawee.client import connect_to_postgres

from batch_jobs.scraper.google_workspace import ScrapeAddOnDetailsJob, scrape_google_workspace_add_ons, \
    get_google_id_from_marketplace_link, sync_scrape_add_on_details, process_add_on_page_response
from batch_jobs.scraper.wayback import wayback_get_all_snapshot_urls, requests_get_with_retry
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


def backfill_google_workspace():
    distinct_links = (BaseGoogleWorkspace
                      .select(BaseGoogleWorkspace.link, BaseGoogleWorkspace.user_count)
                      .distinct()
                      .where(BaseGoogleWorkspace.link.is_null(False))
                      .order_by(BaseGoogleWorkspace.user_count.desc()))
    print("Distinct links count:", distinct_links.count())

    total_scraped = 0
    scraping_start = time.time()
    for add_on in distinct_links:
        wayback_snapshots = []
        for previous_domain in google_workspace_previous_domains():
            target_url = add_on.link.replace("workspace.google.com", previous_domain)
            wayback_snapshots.extend(wayback_get_all_snapshot_urls(target_url=target_url, day_step=1))

        scrape_jobs = []
        for snapshot in wayback_snapshots:
            scrape_jobs.append(ScrapeAddOnDetailsJob(
                url=snapshot.wayback_url(),
                p_date=snapshot.p_date_str(),
                marketplace_link=add_on.link,
                google_id=get_google_id_from_marketplace_link(add_on.link),
            ))

        print(f"Accumulated enough jobs {len(scrape_jobs)}, gonna scrape one-by-one...")
        for scrape_job in scrape_jobs:
            if GoogleWorkspace.exists(scrape_job.google_id, scrape_job.p_date):
                print(f"Skipping as it is already scraped: {scrape_job.url}")
                continue

            print(f"Scraping ({scrape_job.google_id}, {scrape_job.p_date}) from ", scrape_job.url)
            response = requests_get_with_retry(scrape_job.url)
            if response and response.status_code == 200:
                process_add_on_page_response(scrape_job, response.text)
                total_scraped += 1
            else:
                print(f"WARNING: cannot get contents of {scrape_job.url}")

        avg_per_minute = 60 * total_scraped / (time.time() - scraping_start)
        print(f"Total scraped so far: {total_scraped}; on average {avg_per_minute} per minute")
        break


# For Chrome Extensions
# https://chrome.google.com/webstore/detail/kami-pdf-sign-edit-review/iljojpiodmlhoehoecppliohmplbgeij?hl=en&__hstc=20629287.a7f712def3fc231023cd88e3b92265a1.1713973492755.1713973492755.1715724869156.2&__hssc=20629287.1.1715724869156&__hsfp=2560732712


if __name__ == "__main__":
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        backfill_google_workspace()
