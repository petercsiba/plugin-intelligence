import os

from dotenv import load_dotenv
from supawee.client import connect_to_postgres

from supabase.models.data import Plugin, MarketplaceName

load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)

with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
    # TODO(P1, ux): Add top tags to drill down things
    query = Plugin.select(Plugin.main_integrations, Plugin.tags).where(Plugin.marketplace_name == MarketplaceName.GOOGLE_WORKSPACE)
    search_terms = {}
    for plugin in query:
        for list_str in [plugin.main_integrations, plugin.tags]:
            if list_str:
                for item in list_str.split(","):
                    term = item.replace("'", "").strip().capitalize()
                    search_terms[term] = search_terms.get(term, 0) + 1

    # Top Tags
    top_tags = sorted([(v, k) for k, v in search_terms.items()], reverse=True)
    print("Top Tags", top_tags[:50])

    print(len([tag for count, tag in top_tags if count > 1]))
