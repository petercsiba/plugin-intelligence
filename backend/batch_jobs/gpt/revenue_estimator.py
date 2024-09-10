import argparse
import os
import re
import time
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.beta.threads import Message, TextContentBlock
from openai.types.beta.threads.run import Usage
from peewee import fn
from supawee.client import connect_to_postgres

from common.config import OPEN_AI_API_KEY
from common.utils import Timer
from supabase.models.data import Plugin, MarketplaceName

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
def concatenate_assistant_messages(messages: List[Message], created_at_lower_bound: int) -> str:
    concatenated_text = []
    for message in messages:
        if message.role == "assistant":
            for content_block in message.content:
                if isinstance(content_block, TextContentBlock):
                    if message.created_at > created_at_lower_bound:
                        concatenated_text.append(content_block.text.value)
                    else:
                        print(f"Skipping old message created_at {message.created_at}")
                else:
                    print(
                        f"Skipping non-text content block of type {type(content_block)}"
                    )
        elif message.role == "user":
            break  # Stop once we hit the first user message
    return "\n\n".join(reversed(concatenated_text))


#  ["'Translation'", "'Language'", "'Browser Extension'"]
def clean_str_list(str_list: Optional[str]) -> Optional[str]:
    if str_list is None:
        return None
    return str_list.replace("[", "").replace("]", "").replace("'", "").replace('"', "")


def plugin_to_prompt(plugin: Plugin) -> str:
    return f"""
    Plugin name {plugin.name} by {plugin.developer_name}
    has an average rating of {plugin.avg_rating} with {plugin.rating_count} total ratings.
    It has {plugin.user_count} downloads over time by individuals, which can be much higher than actual active individual users.
    Plugin operates withing {clean_str_list(plugin.tags)} spaces in the plugin ecosystem
    and integrates with {clean_str_list(plugin.main_integrations)}.

    It has these pricing tiers {clean_str_list(plugin.pricing_tiers)}.
    The overview summary is {plugin.overview_summary}.
    """
    # TODO(P2, quality): We should add some timeline and backlinks data.


def generate_revenue_estimate(plugin: Plugin,) -> Tuple[Optional[str], Optional[str]]:
    # Subtracting 10 seconds to account for any clock skew
    created_at_lower_bound = int(time.time()) - 10
    # https://platform.openai.com/assistants/asst_1wT0hJmnfnlm8f3kLfHJyVqx
    assistant = direct_openai_client.beta.assistants.retrieve("asst_1wT0hJmnfnlm8f3kLfHJyVqx")

    # Create a thread with messages:
    # if plugin.openai_thread_id is None:
    extra_prompt = ""
    existing_lower_bound = plugin.revenue_lower_bound if plugin.revenue_lower_bound else 0
    existing_upper_bound = plugin.revenue_upper_bound if plugin.revenue_upper_bound else 0
    if max(existing_lower_bound, existing_upper_bound) > 2 * plugin.user_count:
        extra_prompt = (
            # "Lets redo the revenue estimate as it feels off or outdated."
            f"An upper bound revenue estimate over ${2 * plugin.user_count} is very very unlikely. "
            # "If you get such a high estimate, lower your active or "
            # f"paid user assumptions based off the {plugin.user_count} "
            # "installs which might have many abandoned installs or free users. "
        )
    prompt = plugin_to_prompt(plugin) + extra_prompt
    print("Prompt:", prompt)

    new_thread = direct_openai_client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )
    thread_id = new_thread.id
    #    extra_prompt = ""
    # else:
    #    thread_id = plugin.openai_thread_id

    # Create a run
    print(f"creating run for thread {thread_id} and assistant {assistant.id}")
    with Timer("Assistant Run"):
        run = direct_openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant.id,
        )
    chatgpt_usage_pretty_print(run.model, run.usage)

    # If the run is completed, print the messages
    if run.status == "completed":
        messages = direct_openai_client.beta.threads.messages.list(thread_id=thread_id)
        response_text = concatenate_assistant_messages(messages, created_at_lower_bound)
        return response_text, thread_id

    print(f"WARNING: status of run is NOT completed: {run.status}")
    return None, thread_id


# Fuzzy matching to extract lower and upper bounds from generate_revenue_estimate output
def extract_bounds(text: Optional[str], verbose: bool = False) -> Tuple[int, int]:
    if text is None:
        return 0, 0

    # Function to extract all numbers after a specific phrase in a line
    def extract_number_after_phrase(line: str, phrase: str) -> Optional[int]:
        # Find the position of the phrase
        pos = line.lower().find(phrase.lower())
        if pos == -1:
            return None

        # Extract the part of the line after the phrase
        relevant_part = line[pos + len(phrase):]

        # If there's an equals sign, take only the part after the last equals sign
        if '=' in relevant_part:
            relevant_part = relevant_part.split('=')[-1]

        # Remove $ and commas, then find all numbers
        cleaned = re.sub(r'[$,]', '', relevant_part)
        numbers = [int(num) for num in re.findall(r'\d+', cleaned)]

        return max(numbers) if numbers else None

    lower_bound = -1
    upper_bound = -1

    # Split the text into lines and process each line
    for line in text.split('\n'):
        line = line.strip()
        result = None
        if 'lower bound' in line.lower():
            result = extract_number_after_phrase(line, 'lower bound')
            if result is not None:
                lower_bound = result
        elif 'upper bound' in line.lower():
            result = extract_number_after_phrase(line, 'upper bound')
            if result is not None:
                upper_bound = result

        if result is not None and verbose:
            print(f"lower: {lower_bound}, upper: {upper_bound} line: {line}")

    # Error handling
    if lower_bound == -1:
        lower_bound = 0
        print("ERROR: Could not find lower bound")
    if upper_bound == -1:
        upper_bound = 0
        print("ERROR: Could not find upper bound")
    if upper_bound < lower_bound:
        print("WARNING: Upper bound is less than lower bound.")
        upper_bound = lower_bound

    return lower_bound, upper_bound


# TODO(P1, cost): This is a very expensive operation. We should consider running this in Batches (50% off).
#   https://platform.openai.com/docs/guides/batch/model-availability
#   NOTE that batches (of up to 50,000 requests) are only available for ChatCompletion API, not for Assistant API
# Yeah, also considering that people complain that Assistants API pricing is not transparent,
# might as well use the ChatCompletion interface for this task.
# AND remove those plugin $TTM datapoints as they don't seem to be used much
# (we should still disclose them somewhere).
# TODO(P1, quality): For "Free + B2B sales",
#   it outputs 0, 0. We should fix this: 8154 (Barracuda Chromebook Security Extension)
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


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process plugins based on shard and optionally overwrite p_date.')
    parser.add_argument('--shard_id', type=int, required=True, help='ID of the shard to process')
    parser.add_argument('--shard_count', type=int, required=True, help='Total number of shards')
    args = parser.parse_args()

    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        # query_set_unknown = (Plugin
        #          .select()
        #          .where(
        #     (Plugin.revenue_analysis.is_null()) &
        #     (Plugin.marketplace_name == MarketplaceName.CHROME_EXTENSION) &
        #     (fn.MOD(Plugin.id, args.shard_count) == args.shard_id)
        # ))
        query_update_wrong = (Plugin
                 .select()
                 .where(
            (Plugin.revenue_analysis.is_null(False)) &
            ((Plugin.revenue_lower_bound > 2 * Plugin.user_count) | (Plugin.revenue_upper_bound > 2 * Plugin.user_count) | (Plugin.revenue_upper_bound == 0)) &
            (fn.MOD(Plugin.id, args.shard_count) == args.shard_id)
        )
                 .order_by(fn.COALESCE(Plugin.user_count, 0).desc()))
        for p in query_update_wrong:
            print(f"Shard {args.shard_id} / {args.shard_count} is processing plugin id {p.id}: {p.name} ...")
            gpt_generate_revenue_estimate_for_plugin(p, force_update=True)


if __name__ == "__main__":
    main()
