# TODO(P0, devx): We should move to something more robust like Scrapy with Playwright
# https://python.plainenglish.io/combine-playwright-with-scrapy-for-web-scraping-c7c00168f567
import asyncio
from datetime import datetime

from supawee.client import connect_to_postgres

from batch_jobs.scraper.chrome_extensions import scrape_chrome_extensions_in_parallel, get_all_chrome_extensions_from_database
from batch_jobs.scraper.google_workspace import (
    scrape_google_workspace_add_ons, get_all_google_workspace_from_database,
)
from common.config import POSTGRES_DATABASE_URL

# load_dotenv()
# YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
#     "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
# )


if __name__ == "__main__":
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        # Only update the list time-to-time
        # google_workspace_scrape_jobs = get_all_from_marketplace(p_date)
        google_workspace_scrape_jobs = get_all_google_workspace_from_database(p_date)
        print(f"Found {len(google_workspace_scrape_jobs)} Google Workspace to scrape from the database")
        asyncio.run(scrape_google_workspace_add_ons(google_workspace_scrape_jobs))

        # chrome_extension_scrape_jobs = get_all_chrome_extensions_from_marketplace(p_date)
        chrome_extension_scrape_jobs = get_all_chrome_extensions_from_database(p_date)
        print(f"Found {len(chrome_extension_scrape_jobs)} Chrome Extensions to scrape from the database")

        total_jobs = len(chrome_extension_scrape_jobs)
        batch_size = 1000
        # Loop through the jobs in batches of 1000 (might help with memory management)
        for i in range(0, total_jobs, batch_size):
            batch = chrome_extension_scrape_jobs[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1} with {len(batch)} jobs")
            asyncio.run(scrape_chrome_extensions_in_parallel(batch, p_date))
