import os

from dotenv import load_dotenv
from supawee.client import connect_to_postgres

from batch_jobs.gpt.revenue_estimator import extract_bounds
from supabase.models.data import Plugin

load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


def main():
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        query_plugins = (Plugin
                 .select()
                 .where(
            (Plugin.revenue_analysis.is_null(False))
        ))  # .limit(100))

        for p in query_plugins:
            print("Processing plugin", p.id, p.name)
            lower, upper = extract_bounds(p.revenue_analysis, verbose=True)
            p.revenue_lower_bound = lower
            p.revenue_upper_bound = upper
            p.save()


if __name__ == "__main__":
    main()
