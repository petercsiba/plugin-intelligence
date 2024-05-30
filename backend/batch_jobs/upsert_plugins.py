import argparse
import os

from dotenv import load_dotenv
from gpt_form_filler.openai_client import OpenAiClient, BETTER_MODEL
from peewee import fn
from supawee.client import connect_to_postgres

from batch_jobs.common import standardize_url, extract_number_best_effort
from batch_jobs.gpt.revenue_estimator import gpt_generate_revenue_estimate_for_plugin
from batch_jobs.gpt.summarizer import gpt_fill_in_plugin_intel_form, fill_in_plugin_with_form_data, \
    gpt_summarize_reviews
from common.company import standardize_company_name, slugify_company_name
from common.config import POSTGRES_DATABASE_URL, OPEN_AI_API_KEY
from common.gpt_cache import InDatabaseCacheStorage
from supabase.models.base import BaseGoogleWorkspace, BasePlugin
from supabase.models.data import MarketplaceName, Plugin, ChromeExtension

openai_client = OpenAiClient(
    open_ai_api_key=OPEN_AI_API_KEY, cache_store=InDatabaseCacheStorage()
)


def get_p_date(model):
    # Determine the latest p_date, either from the argument or the database
    if args.p_date:
        latest_date = args.p_date
    else:
        latest_date = model.select(
            fn.MAX(model.p_date)
        ).scalar()
    print(f"P_DATE set to {latest_date}")
    return latest_date


# Function to convert a workspace row to text
# NOTE: The overview will be passed in as a separate variable
def chrome_extension_to_prompt_header(chrome_extension: ChromeExtension) -> str:
    return f"""
============================
The plugin name is {chrome_extension.name}
and provided description is {chrome_extension.description}
    """


def upsert_chrome_extensions(p_date: str, force_update_gpt: bool = False):
    print("Upserting Chrome Extensions for p_date:", p_date, "force_update_gpt:", force_update_gpt)
    # TODO(P1, cost): Seems like this is a slow query taking ~50% of all DB cpu. Good for now.
    query = (
        ChromeExtension.select()
        .where(
            (ChromeExtension.p_date == p_date) &
            (~ChromeExtension.google_id.in_(
                Plugin.select(Plugin.marketplace_id)
            ))
        )
        .order_by(fn.COALESCE(ChromeExtension.user_count, -1).desc())
    )

    # Loop through each row and apply the OpenAI API
    done_so_far = 0
    for chrome_extension in query:
        chrome_extension: ChromeExtension  # type hint

        # Using get_or_create to find or create the record
        # Yes, using .insert with on_conflict_update is more effective but ChatGPT is the slow part here so shrug.
        plugin, created = BasePlugin.get_or_create(
            marketplace_name=MarketplaceName.CHROME_EXTENSION,
            marketplace_id=chrome_extension.google_id,
        )
        plugin: BasePlugin  # type hint
        # Copy scraped data to the Plugin table
        plugin.name = chrome_extension.name
        plugin.logo_link = chrome_extension.logo_link
        plugin.marketplace_link = chrome_extension.link
        plugin.avg_rating = extract_number_best_effort(chrome_extension.rating)
        plugin.rating_count = chrome_extension.rating_count
        plugin.user_count = chrome_extension.user_count
        plugin.developer_link = standardize_url(chrome_extension.developer_link)
        # TODO(P0, ux): Better deal with unknown company names
        company_name = standardize_company_name(chrome_extension.developer_name)
        plugin.developer_name = company_name
        plugin.company_slug = slugify_company_name(company_name)

        # TODO(P3, devx) The above is the same as Google Workspace, so we can refactor this into a function
        plugin.developer_email = chrome_extension.developer_email
        plugin.developer_address = chrome_extension.developer_address

        # Add derived stuff to the Plugin table
        if plugin.user_count > 1000:
            if plugin.overview_summary is None or force_update_gpt:
                extra_prompt_header = chrome_extension_to_prompt_header(chrome_extension)
                form_data = gpt_fill_in_plugin_intel_form(
                    openai_client=openai_client,
                    overview=chrome_extension.overview,
                    extra_prompt_header=extra_prompt_header
                )
                fill_in_plugin_with_form_data(plugin, form_data)
        else:
            print(f"Plugin id: {plugin.id} skipped Plugin Intel Form (has {chrome_extension.user_count} users)")

        # NOTE: We do NOT summarize reviews as we ain't scraping them (only shows 3 most recent ones)
        #   There are a few more recent ones on the /reviews page, but ideally we would like the "most relevant" ones.

        plugin.save()

        done_so_far += 1
        print(f"Plugin id: {plugin.id} saved (has {chrome_extension.user_count} users); So far done: {done_so_far}")
        if done_so_far % 100 == 0:
            print(openai_client.sum_up_prompt_stats().pretty_print())


# Function to convert a workspace row to text
# NOTE: The overview will be passed in as a separate variable
def workspace_row_to_prompt_header(row: BaseGoogleWorkspace) -> str:
    pricing = ""
    if row.pricing != "Not available":
        pricing = f" and is provided as {row.pricing}"

    return f"""
============================
The plugin name is {row.name} {pricing}
    """


def upsert_google_workspace_add_ons(p_date: str, force_update_gpt: bool = False):
    print("Upserting Google Workspace Addons for p_date:", p_date, "force_update_gpt:", force_update_gpt)
    query = (
        BaseGoogleWorkspace.select()
        .where(
            (BaseGoogleWorkspace.p_date == p_date) &
            # Exclude plugins that are already created in the Plugin table
            (~BaseGoogleWorkspace.google_id.in_(
                Plugin.select(Plugin.marketplace_id)
            ))
        )
        .order_by(fn.COALESCE(BaseGoogleWorkspace.user_count, -1).desc())
    )

    # Loop through each row and apply the OpenAI API
    done_so_far = 0
    for add_on_row in query:
        add_on_row: BaseGoogleWorkspace  # type hint

        # Using get_or_create to find or create the record
        # Yes, using .insert with on_conflict_update is more effective but ChatGPT is the slow part here so shrug.
        plugin, created = BasePlugin.get_or_create(
            marketplace_name=MarketplaceName.GOOGLE_WORKSPACE,
            marketplace_id=add_on_row.google_id,
        )
        plugin: BasePlugin  # type hint
        # Copy scraped data to the Plugin table
        plugin.name = add_on_row.name
        plugin.logo_link = add_on_row.logo_link
        plugin.marketplace_link = add_on_row.link
        plugin.avg_rating = extract_number_best_effort(add_on_row.rating)
        plugin.rating_count = add_on_row.rating_count
        plugin.user_count = add_on_row.user_count
        plugin.developer_link = standardize_url(add_on_row.developer_link)
        company_name = standardize_company_name(add_on_row.developer_name)
        plugin.developer_name = company_name
        plugin.company_slug = slugify_company_name(company_name)

        # Add derived stuff to the Plugin table
        # For Chrome Extensions, only about 20% have more than 1000 users.
        if plugin.user_count > 1000:
            if plugin.overview_summary is None or force_update_gpt:
                extra_prompt_header = workspace_row_to_prompt_header(add_on_row)
                form_data = gpt_fill_in_plugin_intel_form(openai_client=openai_client, overview=add_on_row.overview, extra_prompt_header=extra_prompt_header)
                fill_in_plugin_with_form_data(plugin, form_data)
        else:
            print(f"Plugin id: {plugin.id} skipped Plugin Intel Form (has {add_on_row.user_count} users)")

        # Summarize reviews if there are enough reviews and ratings
        if (
            plugin.rating_count
            and plugin.rating_count > 20
            and add_on_row.reviews.count("ReviewData") > 4
        ):
            if plugin.reviews_summary is None or force_update_gpt:
                plugin.reviews_summary = gpt_summarize_reviews(openai_client=openai_client, reviews=add_on_row.reviews)
        else:
            print(f"Plugin id: {plugin.id} skipped Reviews Summary (has {add_on_row.rating_count} ratings)")

        plugin.save()

        done_so_far += 1
        print(f"Plugin id: {plugin.id} saved (has {add_on_row.user_count} users); So far done: {done_so_far}")
        if done_so_far % 100 == 0:
            print(openai_client.sum_up_prompt_stats().pretty_print())


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)

# Set up argument parser
parser = argparse.ArgumentParser(description='Overwrite p_date if provided.')
parser.add_argument('--p_date', type=str, help='The date to overwrite p_date')
args = parser.parse_args()


# TODO(P1, cost): This is somewhat expensive operation.
#   We should separate out the field updates and the OpenAI API calls.
if __name__ == "__main__":
    #with connect_to_postgres(POSTGRES_DATABASE_URL):
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        # google_workspace_p_date = get_p_date(BaseGoogleWorkspace)
        # upsert_google_workspace_add_ons(google_workspace_p_date)
        # print(openai_client.sum_up_prompt_stats().pretty_print())

        chrome_extension_p_date = "2024-05-29"  # get_p_date(ChromeExtension)
        upsert_chrome_extensions(chrome_extension_p_date)
        print(openai_client.sum_up_prompt_stats().pretty_print())



