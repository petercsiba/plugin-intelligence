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
        asyncio.run(scrape_chrome_extensions_in_parallel(chrome_extension_scrape_jobs, p_date))
