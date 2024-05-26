import json
import os

from dotenv import load_dotenv
from peewee import fn
from supawee.client import connect_to_postgres

from batch_jobs.dataforseo_driver import (
    get_backlinks_bulk_backlinks_count_live, get_result_items_safe,
)
from supabase.models.data import Plugin

load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)

# TODO(P1, cost): This is somewhat expensive operation.
#   We should separate out the field updates and the OpenAI API calls.
if __name__ == "__main__":
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        plugins = list(Plugin.select(Plugin.marketplace_link).where(Plugin.user_count > 100).order_by(fn.COALESCE(Plugin.user_count, -1).desc()))

    links = [plugin.marketplace_link for plugin in plugins if plugin.marketplace_link]
    print("Found links:", len(links))

    BATCH_SIZE = 1000
    # Batch links into groups of BATCH_SIZE and retrieve backlinks
    batched_links = [
        links[i: i + BATCH_SIZE] for i in range(0, len(links), BATCH_SIZE)
    ]
    all_backlinks = {}
    filepath_prefix = f"batch_jobs/backlinks_data/backlinks-count-"
    for i, batch in enumerate(batched_links):
        # Up to 1000 I believe, pricing is $0.02 + items * $0.00003 (so 1,000 items is $0.05)
        api_response = get_backlinks_bulk_backlinks_count_live(target_urls=batch)
        items = get_result_items_safe(api_response, expected_items_count=len(batch))
        backlinks = {item["target"]: item["backlinks"] for item in items}
        all_backlinks.update(backlinks)

        filepath_batch = filepath_prefix + f"batch-{i}.json"
        with open(filepath_batch, "w") as f:
            json.dump(items, f)

    with open(filepath_prefix + "all.json", "w") as f:
        json.dump(all_backlinks, f)
        # TODO(P0): Add it to our database
