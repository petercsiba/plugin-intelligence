import asyncio
from datetime import datetime

from supawee.client import connect_to_postgres

from batch_jobs.chrome_extensions import get_all_chrome_extensions
from batch_jobs.google_workspace import get_all_google_workspace_add_ons
from common.config import POSTGRES_DATABASE_URL

if __name__ == "__main__":
    # We will ignore the complexity of timezones
    p_date = datetime.today().strftime("%Y-%m-%d")
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        asyncio.run(get_all_chrome_extensions(p_date))
        asyncio.run(get_all_google_workspace_add_ons(p_date))
