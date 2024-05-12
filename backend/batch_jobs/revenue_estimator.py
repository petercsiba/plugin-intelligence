import re
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from gpt_form_filler.openai_client import OpenAiClient
from openai import OpenAI
from openai.types.beta.threads import Message, TextContentBlock
from openai.types.beta.threads.run import Usage
from supawee.client import connect_to_postgres

from common.config import OPEN_AI_API_KEY, POSTGRES_DATABASE_URL
from common.gpt import InDatabaseCacheStorage
from common.utils import Timer
from supabase.models.base import BaseGoogleWorkspace
from supabase.models.data import Plugin, MarketplaceName, Plugin

openai_client = OpenAiClient(
    open_ai_api_key=OPEN_AI_API_KEY,
    cache_store=InDatabaseCacheStorage()
)

google_ids = ["619840861140", "258179390912"]


@dataclass
class RevenueEstimatorInputs:
    name: str
    developer_name: str
    rating: float
    rating_count: int
    user_count: int
    link: str
    listing_updated: str
    pricing_category: str
    pricing_tiers: str
    overview_summary: str
    search_terms: str
    # TODO: backlinks

    def to_prompt(self):
        return f"""
        Plugin name {self.name} by {self.developer_name} has a rating of {self.rating} with {self.rating_count} ratings.
        It has {self.user_count} users and was last updated on {self.listing_updated}.
        You can find it by searching {self.search_terms} on the Google Workspace Marketplace.
        The pricing category is {self.pricing_category} with pricing tiers {self.pricing_tiers}.
        The overview summary is {self.overview_summary} and you can find more information at {self.link}.
        """


def add_on_to_inputs(plugin: Plugin, scraped_data: BaseGoogleWorkspace) -> RevenueEstimatorInputs:
    return RevenueEstimatorInputs(
        name=scraped_data.name,
        developer_name=scraped_data.developer_name,
        rating=scraped_data.rating,
        rating_count=scraped_data.rating_count,
        user_count=scraped_data.user_count,
        link=scraped_data.link,
        listing_updated=scraped_data.listing_updated,
        pricing_category=scraped_data.pricing,
        pricing_tiers=plugin.pricing_tiers,
        overview_summary=plugin.overview_summary,
        search_terms=plugin.search_terms
    )


client = OpenAI(api_key=OPEN_AI_API_KEY)


def chatgpt_usage_pretty_print(model: str, usage: Usage):
    input_tok = usage.prompt_tokens
    output_tok = usage.completion_tokens
    cost = chatgpt_cost_estimate_millionth_dollar(model, input_tok, output_tok) / 1_000_000
    print(f"${cost} for model: {model} prompt tokens: {input_tok}, completion tokens: {output_tok}")


def chatgpt_cost_estimate_millionth_dollar(model, input_tok, output_tok):
    # https://openai.com/pricing
    if model.startswith("gpt-4-turbo"):
        return 10 * input_tok + 30 * output_tok
    if model.startswith("gpt-4-32k"):
        return 60 * input_tok + 120 * output_tok
    if model.startswith("gpt-4"):
        return 30 * input_tok + 60 * output_tok
    if model.startswith("gpt-3.5-turbo-instruct"):
        return 1.5 * input_tok + 2 * output_tok
    if model.startswith("gpt-3.5-turbo"):
        return 0.5 * input_tok + 1.5 * output_tok

    print(f"WARNING: unknown pricing for model {model}")
    return 0


# Function to concatenate messages from the assistant until a user message is found
def concatenate_assistant_messages(messages: List[Message]) -> str:
    concatenated_text = []
    for message in messages:
        if message.role == "assistant":
            for content_block in message.content:
                if isinstance(content_block, TextContentBlock):
                    concatenated_text.append(content_block.text.value)
                else:
                    print(f"Skipping non-text content block of type {type(content_block)}")
        elif message.role == "user":
            break  # Stop once we hit the first user message
    return "\n\n".join(reversed(concatenated_text))


def generate_revenue_estimate(inputs: RevenueEstimatorInputs) -> Tuple[Optional[str], Optional[str]]:
    # https://platform.openai.com/assistants/asst_1wT0hJmnfnlm8f3kLfHJyVqx
    assistant = client.beta.assistants.retrieve("asst_1wT0hJmnfnlm8f3kLfHJyVqx")

    # Create a thread with messages:
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": inputs.to_prompt(),
            }
        ]
    )

    # Create a run
    print(f"creating run for thread {thread.id} and assistant {assistant.id}")
    with Timer("Assistant Run"):
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
    chatgpt_usage_pretty_print(run.model, run.usage)

    # If the run is completed, print the messages
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = concatenate_assistant_messages(messages)
        return response_text, thread.id

    print(f"WARNING: status of run is NOT completed: {run.status}")
    return None, thread.id


# Fuzzy matching to extract lower and upper bounds from generate_revenue_estimate output
def extract_bounds(text: Optional[str]):
    # Regular expression pattern to capture amounts following "Lower" or "Upper" keywords
    # Adjusted pattern to capture bullet points, bold markers, and flexible spacing
    # Examples:
    # - **Lower** Bound: $1,000
    # * Upper Bound: $2,000
    # - **Lower Bound**: Assuming a slight decrease in conversion rates — $10,000
    pattern = r"(?i)(lower|upper)[^\$]*\$(\d+(?:,\d+)*)"

    # Find all matches using the pattern
    matches = re.findall(pattern, str(text))

    def clean_amount(int_str: str) -> int:
        """Helper function to remove commas and convert to integer."""
        return int(int_str.replace(",", ""))

    # Initialize variables to hold the bounds
    lower_bound = 0
    upper_bound = 0

    # Process the matches and assign to appropriate variables
    for role, amount in matches:
        if role.lower() == "lower":
            # We do `max` since the revenue analysis can do lower/upper bounds on multiple parameters,
            # think ARPU or monthly revenue, while we want to capture the annual revenue.
            lower_bound = max(lower_bound, clean_amount(amount))
        elif role.lower() == "upper":
            upper_bound = max(lower_bound, clean_amount(amount))

    if lower_bound == 0 or upper_bound == 0:
        print("ERROR: Could not find both lower and upper bounds.")

    return lower_bound, upper_bound


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get("YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL")


def main():
    # TODO(P1, cost): This is a very expensive operation. We should consider running this in Batches (50% off).
    #   https://platform.openai.com/docs/guides/batch/model-availability
    #   NOTE that batches (of up to 50,000 requests) are only available for ChatCompletion API, not for Assistant API
    # Yeah, also considering that people complain that Assistants API pricing is not transparent,
    # might as well use the ChatCompletion interface for this task.
    # AND remove those plugin $TTM datapoints as they don't seem to be used much
    # (we should still disclose them somewhere).
    # with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
    with connect_to_postgres(POSTGRES_DATABASE_URL):
        for plugin in Plugin.select().where(Plugin.revenue_analysis.is_null()).limit(1):

            scraped_data = plugin.get_scraped_data()
            inputs = add_on_to_inputs(plugin, scraped_data)
            revenue_analysis, thread_id = generate_revenue_estimate(inputs=inputs)
            lower_bound, upper_bound = extract_bounds(revenue_analysis)

            # TODO(ux, P2): Might be nice to do a few more prompts to get more comprehensive report,
            #   especially for a higher ranking plugin.

            plugin.revenue_analysis = revenue_analysis
            plugin.openai_thread_id = thread_id
            plugin.revenue_lower_bound = lower_bound
            plugin.revenue_upper_bound = upper_bound
            plugin.save()

    print(openai_client.sum_up_prompt_stats().pretty_print())


if __name__ == "__main__":
    main()
