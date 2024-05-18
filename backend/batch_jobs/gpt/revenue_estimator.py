import re
from typing import List, Optional, Tuple

from openai import OpenAI
from openai.types.beta.threads import Message, TextContentBlock
from openai.types.beta.threads.run import Usage

from common.config import OPEN_AI_API_KEY
from common.utils import Timer
from supabase.models.data import Plugin


# TODO(P1, devx): Add assistant support OR migrate to ChatCompletion API
direct_openai_client = OpenAI(api_key=OPEN_AI_API_KEY)


def chatgpt_usage_pretty_print(model: str, usage: Usage):
    input_tok = usage.prompt_tokens
    output_tok = usage.completion_tokens
    cost = (
        chatgpt_cost_estimate_millionth_dollar(model, input_tok, output_tok) / 1_000_000
    )
    print(
        f"${cost} for model: {model} prompt tokens: {input_tok}, completion tokens: {output_tok}"
    )


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
                    print(
                        f"Skipping non-text content block of type {type(content_block)}"
                    )
        elif message.role == "user":
            break  # Stop once we hit the first user message
    return "\n\n".join(reversed(concatenated_text))


def plugin_to_prompt(plugin: Plugin) -> str:
    return f"""
    Plugin name {plugin.name} by {plugin.developer_name}
    has an average rating of {plugin.avg_rating} with {plugin.rating_count} total ratings.
    It has {plugin.user_count} downloads over time, this can be much higher than actual active users.
    You can find it by searching {plugin.tags} on the Google Workspace Marketplace.
    It has these pricing tiers {plugin.pricing_tiers}.
    The overview summary is {plugin.overview_summary}.
    """
    # TODO(P2, quality): We should add some timeline and backlinks data.


def generate_revenue_estimate(plugin: Plugin,) -> Tuple[Optional[str], Optional[str]]:
    # https://platform.openai.com/assistants/asst_1wT0hJmnfnlm8f3kLfHJyVqx
    assistant = direct_openai_client.beta.assistants.retrieve("asst_1wT0hJmnfnlm8f3kLfHJyVqx")

    # Create a thread with messages:
    thread = direct_openai_client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": plugin_to_prompt(plugin),
            }
        ]
    )

    # Create a run
    print(f"creating run for thread {thread.id} and assistant {assistant.id}")
    with Timer("Assistant Run"):
        run = direct_openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
    chatgpt_usage_pretty_print(run.model, run.usage)

    # If the run is completed, print the messages
    if run.status == "completed":
        messages = direct_openai_client.beta.threads.messages.list(thread_id=thread.id)
        response_text = concatenate_assistant_messages(messages)
        return response_text, thread.id

    print(f"WARNING: status of run is NOT completed: {run.status}")
    return None, thread.id


# Fuzzy matching to extract lower and upper bounds from generate_revenue_estimate output
def extract_bounds(text: Optional[str]) -> Tuple[int, int]:
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


# TODO(P1, cost): This is a very expensive operation. We should consider running this in Batches (50% off).
#   https://platform.openai.com/docs/guides/batch/model-availability
#   NOTE that batches (of up to 50,000 requests) are only available for ChatCompletion API, not for Assistant API
# Yeah, also considering that people complain that Assistants API pricing is not transparent,
# might as well use the ChatCompletion interface for this task.
# AND remove those plugin $TTM datapoints as they don't seem to be used much
# (we should still disclose them somewhere).
def gpt_generate_revenue_estimate_for_plugin(plugin: Plugin, force_update=False) -> None:
    if plugin.revenue_analysis and not force_update:
        print(f"Skipping plugin {plugin.id} as it already has revenue analysis.")
        return

    revenue_analysis, thread_id = generate_revenue_estimate(plugin=plugin)
    lower_bound, upper_bound = extract_bounds(revenue_analysis)

    # TODO(ux, P2): Might be nice to do a few more prompts to get more comprehensive report,
    #   especially for a higher ranking plugin.

    plugin.revenue_analysis = revenue_analysis
    plugin.openai_thread_id = thread_id
    plugin.revenue_lower_bound = lower_bound
    plugin.revenue_upper_bound = upper_bound
    plugin.save()

    print(f"Saved revenue analysis for plugin {plugin.id} with bounds {lower_bound} - {upper_bound}")
