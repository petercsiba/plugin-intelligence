import asyncio
from datetime import datetime

from supawee.client import connect_to_postgres

from batch_jobs.scraper.chrome_extensions import get_all_chrome_extensions_from_marketplace
from batch_jobs.scraper.google_workspace import (
    scrape_google_workspace_add_ons,
    get_all_from_marketplace,
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
        # TODO(P1, devx): Just get distinct links from the DB,
        #   and maybe every-week do a full re-scrape of the listing pages.
        scrape_job_list = get_all_from_marketplace(p_date)
        asyncio.run(scrape_google_workspace_add_ons(scrape_job_list))

        asyncio.run(get_all_chrome_extensions_from_marketplace(p_date))
