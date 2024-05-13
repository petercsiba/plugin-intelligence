import os
from typing import Optional, Any

from dotenv import load_dotenv
from gpt_form_filler.form import FieldDefinition, FormDefinition
from gpt_form_filler.openai_client import OpenAiClient
from peewee import fn
from supawee.client import connect_to_postgres
from gpt_form_filler.openai_client import CHEAPEST_MODEL

from common.config import POSTGRES_DATABASE_URL, OPEN_AI_API_KEY
from common.gpt import InDatabaseCacheStorage
from common.utils import now_in_utc
from supabase.models.base import BaseGoogleWorkspace, BasePlugin
from supabase.models.data import MarketplaceName

plugin_intel_form_fields = [
    # This is the most important as oftentimes app pricing is buried in the overview summary.
    FieldDefinition(
        name="pricing_tiers",
        field_type="text",
        label="Pricing Tiers",
        description=(
            "Extract all mentioned pricing tiers as a list of 'pricing tier and monthly cost'."
        ),
    ),
    FieldDefinition(
        name="lowest_paid_tier",
        field_type="number",
        label="Lowest Paid Tier",
        description="The lowest pricing tier monthly cost, 0 if all tiers are free or not available.",
    ),
    FieldDefinition(
        name="search_terms",
        field_type="text",
        label="Search Terms",
        description="Generate the top 10 search keywords for this plugin",
    ),
    FieldDefinition(
        name="tags",
        field_type="text",
        label="Tags",
        description="Enlist 2 to 5 tags to categorize this plugin",
    ),
    FieldDefinition(
        name="main_integrations",
        field_type="text",
        label="Main Integrations",
        description="Enumerate up to 10 largest non-Google integrations for this plugin",
    ),
    FieldDefinition(
        name="elevator_pitch",
        field_type="text",
        label="Elevator Pitch",
        description="Come up with a one line elevator pitch for this plugin",
    ),
]

plugin_intel_form = FormDefinition("plugin_intel", plugin_intel_form_fields)
extra_fieldnames = [field.name for field in plugin_intel_form_fields]

openai_client = OpenAiClient(
    open_ai_api_key=OPEN_AI_API_KEY,
    cache_store=InDatabaseCacheStorage()
)


# Function to convert a workspace row to text
def workspace_row_to_prompt(row: BaseGoogleWorkspace, overview_summary: str):
    pricing = ""
    if row.pricing != "Not available":
        pricing = f" and is provided as {row.pricing}"

    return f"""
============================
The plugin name is {row.name} {pricing}
Let me tell you much more about the plugin: {overview_summary}
    """

#     return f"""
# Plugin info:
# * Name: {row.name}
# * Description: {row.description}
# * Developer Name: {row.developer_name}
# * Last updated: {row.listing_updated}
# * Description: {row.description}
# * Pricing Category: {row.pricing}
# * Permissions: {row.permissions}
# * Long-form overview: {row.overview}
# """


# TODO: we should re-use this for all stuff generated by chatGPT
# https://chat.openai.com/share/ade62ab0-d1d7-4d17-bc60-89e42b67bfb3
def parse_to_list(input_str: Optional[Any]):
    if input_str is None:
        return None

    if isinstance(input_str, list):
        return ", ".join(input_str)

    items = []

    # Split the input string by lines
    lines = str(input_str).strip().splitlines()

    for line in lines:
        # Check if the line has asterisks or commas, handle both cases
        if '*' in line:
            # Handle lines prefixed with '*'
            items.extend([item.strip() for item in line.split('*') if item.strip()])
        elif ',' in line:
            items.extend([item.strip() for item in line.split(',') if item.strip()])
        elif ';' in line:
            items.extend([item.strip() for item in line.split(';') if item.strip()])
        else:
            items.append(line)

    cleaned_items = []
    for item in items:
        cleaned_item = item.strip()
        if cleaned_item:
            cleaned_items.append(item)

    return ", ".join(repr(item) for item in cleaned_items)


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get("YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL")


# TODO(P1, cost): This is a very expensive operation. We should consider running this in batches.
#   https://platform.openai.com/docs/guides/batch/model-availability
#with connect_to_postgres(POSTGRES_DATABASE_URL):
with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
    latest_date = BaseGoogleWorkspace.select(fn.MAX(BaseGoogleWorkspace.p_date)).scalar()
    print(f"LATEST P_DATE is {latest_date}")

    query = BaseGoogleWorkspace.select().where(BaseGoogleWorkspace.p_date == latest_date).order_by(fn.COALESCE(BaseGoogleWorkspace.user_count, -1).desc())

    # Loop through each row and apply the OpenAI API
    for add_on_row in query.limit(200):
        # Although GPT-4 was able to fill_in_form, GPT-3.5 requires more handholding so we pre-process the info.
        summary_prompt = f"""
        Summarize this plugin description,
        while making sure you persist pricing information, who is it for and all relevant capabilities.
        My note is:  {add_on_row.overview}
        """
        overview_summary = openai_client.run_prompt(prompt=summary_prompt, model=CHEAPEST_MODEL)

        # Fill in the form using OpenAI
        form_data_obj, err = openai_client.fill_in_form(
            form=plugin_intel_form,
            text=workspace_row_to_prompt(add_on_row, overview_summary),
            model=CHEAPEST_MODEL,
        )

        if err:
            print(f"ERROR: processing BaseGoogleWorkspace google_id {add_on_row.google_id}: {err}")
            continue

        form_data = form_data_obj.to_dict()

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
        plugin.rating = add_on_row.rating
        plugin.rating_count = add_on_row.rating_count
        plugin.user_count = add_on_row.user_count

        # Add new stuff to the Plugin table
        plugin.pricing_tiers = parse_to_list(form_data.get('pricing_tiers'))
        plugin.lowest_paid_tier = form_data.get('lowest_paid_tier')
        if plugin.lowest_paid_tier == 0:
            plugin.lowest_paid_tier = None
        print("lowest_paid_tier", plugin.lowest_paid_tier)

        plugin.main_integrations = parse_to_list(form_data.get('main_integrations'))
        plugin.overview_summary = overview_summary
        plugin.elevator_pitch = form_data.get('elevator_pitch')
        plugin.tags = parse_to_list(form_data.get('tags'))
        plugin.updated_at = now_in_utc()  # TODO: why not working?

        search_terms = form_data.get('search_terms')
        print("search_terms", search_terms)
        if search_terms:
            search_terms = str(search_terms).lower()
        plugin.search_terms = parse_to_list(search_terms)

        print(f"Plugin id: {plugin.id} saved ({add_on_row.user_count} users)")
        plugin.save()


print(openai_client.sum_up_prompt_stats().pretty_print())
