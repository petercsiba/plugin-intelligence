from typing import Dict, Optional

from gpt_form_filler.form import FormDefinition, FieldDefinition
from gpt_form_filler.openai_client import CHEAPEST_MODEL, OpenAiClient

from batch_jobs.common import extract_list_best_effort
from supabase.models.base import BasePlugin

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
    # FieldDefinition(
    #     name="search_terms",
    #     field_type="text",
    #     label="Search Terms",
    #     description="Generate the top 10 search keywords for this plugin",
    # ),
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
        description="Come up with a one line elevator pitch why you should install this plugin",
    ),
]

plugin_intel_form = FormDefinition("plugin_intel", plugin_intel_form_fields)
extra_fieldnames = [field.name for field in plugin_intel_form_fields]


# NOTE: "overview_summary" and "__error__" are added to the "plugin_intel_form" FormDefinition
# TODO(P2, devx): Ideally this should just take a plugin object BUT we do NOT store the full overview in the database :/
def gpt_fill_in_plugin_intel_form(openai_client: OpenAiClient, overview: str, extra_prompt_header: str) -> Dict[str, str]:
    # Although GPT-4 is able to fill_in_form directly, GPT-3.5 requires more handholding so we pre-process the info.
    summary_prompt = f"""
    Summarize this plugin description,
    while making sure you persist pricing information, who is it for and all relevant capabilities.
    My note is:  {overview}
    """
    overview_summary = openai_client.run_prompt(
        prompt=summary_prompt, model=CHEAPEST_MODEL, print_prompt=False
    )
    # Fill in the form using OpenAI
    form_data_obj, err = openai_client.fill_in_form(
        form=plugin_intel_form,
        text=extra_prompt_header + "\n===== overview summary:\n" + overview_summary,
        model=CHEAPEST_MODEL,
        print_prompt=False,
    )
    if err:
        return {"overview_summary": overview_summary, "__error__": err}

    form_data = form_data_obj.to_dict()
    form_data["overview_summary"] = overview_summary
    form_data["__error__"] = None
    return form_data


def fill_in_plugin_with_form_data(plugin: BasePlugin, form_data: Dict[str, str]) -> None:
    plugin.overview_summary = form_data.get("overview_summary")
    if form_data.get("__error__"):
        print(f"Error while filling in form: {form_data.get('__error__')}")
        return

    plugin.pricing_tiers = extract_list_best_effort(form_data.get("pricing_tiers"))
    plugin.lowest_paid_tier = form_data.get("lowest_paid_tier")
    if plugin.lowest_paid_tier == 0:
        plugin.lowest_paid_tier = None

    plugin.main_integrations = extract_list_best_effort(form_data.get("main_integrations"))
    plugin.elevator_pitch = form_data.get("elevator_pitch")
    plugin.tags = extract_list_best_effort(form_data.get("tags"))


def gpt_summarize_reviews(openai_client: OpenAiClient, reviews: str) -> Optional[str]:
    # We do check for enough ReviewsData, but empty reviews leads "this vacuum is nice but quite noisy"
    if reviews is None or len(reviews) < 100:
        print(f"Reviews are too short: {reviews}")
        return None

    # add_on_row.reviews is formatted as (for historical reasons):
    # [ReviewData(name='John Doe', rating=5, date='2022-01-01', review='Great app!'), ...]
    cleaned_reviews = _remove_excessive_repetitions(reviews, chunk_size=12, max_repetitions=2)
    reviews_summary_prompt = f"""
    Summarize these customer reviews to fill in a section "Customers Say":  {cleaned_reviews}
    """
    return openai_client.run_prompt(
        reviews_summary_prompt, model=CHEAPEST_MODEL, print_prompt=False
    )


def _remove_excessive_repetitions(s, chunk_size=12, max_repetitions=2):
    # Dictionary to count occurrences of each chunk
    chunk_counts = {}
    i = 0
    output = []

    while i < len(s):
        # Extract a chunk of specified size
        chunk = s[i:i+chunk_size]

        if chunk in chunk_counts:
            # Increment the count of the chunk
            chunk_counts[chunk] += 1
        else:
            # Add the chunk to the dictionary with an initial count of 1
            chunk_counts[chunk] = 1

        # Append the chunk to the output only if it hasn't exceeded the allowed repetitions
        if chunk_counts[chunk] <= max_repetitions:
            output.append(chunk)

        # Move to the next chunk
        i += chunk_size

    # Join the output list back into a string
    return ''.join(output)
