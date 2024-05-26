# TODO Try competitor backlinks https://dataforseo.com/help-center/find-competitors-by-backlinks
# https://api.dataforseo.com/v3/dataforseo_labs/google/historical_bulk_traffic_estimation/live

import json
import os
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, urlunparse

import requests
from dotenv import load_dotenv
from peewee import fn
from pydantic import BaseModel
from supawee.client import connect_to_postgres

from supabase.models.data import Plugin

load_dotenv()
TOKEN = os.environ.get("DATAFORSEO_API_TOKEN")  # base64 encoded "login:password"
# Set the headers, including authorization and content type
HEADERS = {"Authorization": "Basic " + TOKEN, "Content-Type": "application/json"}
BASE_URL = "https://api.dataforseo.com/v3/"


class TaskData(BaseModel):
    api: str
    function: str
    target: Optional[str] = None
    internal_list_limit: Optional[int] = None
    backlinks_status_type: Optional[str] = None
    include_subdomains: Optional[bool] = None
    targets: Optional[List[str]] = None


class TaskResult(BaseModel):
    items_count: Optional[int] = None
    items: Optional[List[Dict[str, Any]]] = None


class Task(BaseModel):
    id: str
    status_code: int
    status_message: str
    time: str
    cost: float
    result_count: int
    path: List[str]
    data: TaskData
    # Unsure in which cases there are multiple
    result: List[TaskResult]


class ApiResponse(BaseModel):
    version: str
    status_code: int
    status_message: str
    time: str
    cost: float
    tasks_count: int
    tasks_error: int
    tasks: Optional[List[Task]] = None


def post_request(api_path: str, json_payload: Union[dict, list]) -> ApiResponse:
    url = f"{BASE_URL}{api_path}"
    json_payload_str = json.dumps(json_payload)
    response = requests.post(url, headers=HEADERS, data=json_payload_str)
    # print(response.text)
    json_response = json.loads(response.text)
    api_response = ApiResponse(**json_response)
    print(f"response status: {api_response.status_code}: {api_response.status_message}")
    return api_response


# DataForSEO needs "/", e.g. https://www.ablebits.com -> 0 backlinks, while https://www.ablebits.com/ -> 2665 backlinks
def ensure_slash_after_tld(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)

    # Check if the path is empty or just '/'
    if not parsed_url.path or parsed_url.path == "/":
        # Add a trailing slash if there isn't one
        path = "/"
    else:
        # Otherwise, keep the path as is
        path = parsed_url.path

    # Reconstruct the URL with the updated path
    # TODO: consider removing params
    cleaned_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )

    return str(cleaned_url)


def get_backlinks_summary_live(target_url: str) -> ApiResponse:
    json_payload = [
        {
            "target": ensure_slash_after_tld(target_url),
            "limit": 1000,
            "internal_list_limit": 10,
            "backlinks_status_type": "live",
            "include_subdomains": True,
        },
    ]
    return post_request("backlinks/summary/live", json_payload)


# This feels superior to labs_competitors_domain
def get_backlinks_competitors_live(
    target_url: str, min_rank: int = 10, limit: int = 25
) -> ApiResponse:
    json_payload = [
        {
            "target": ensure_slash_after_tld(target_url),
            "filters": ["rank", ">", min_rank],
            "order_by": ["rank,desc"],
            "limit": limit,
        },
    ]
    return post_request("backlinks/competitors/live", json_payload)


# Lists all backlinks
def get_backlinks_backlinks_live(target_url: str) -> ApiResponse:
    json_payload = [
        {
            "target": ensure_slash_after_tld(target_url),
            "limit": 1000,
            # "internal_list_limit": 10,
            "offset": 0,
            "backlinks_status_type": "live",
            "include_subdomains": True,
            "mode": "as_is",
        }
    ]
    return post_request("backlinks/backlinks/live", json_payload)


def get_backlinks_bulk_backlinks_count_live(target_urls: list[str]) -> ApiResponse:
    print(f"get_backlinks_bulk_backlinks_live for {len(target_urls)} urls")
    json_payload = [{"targets": [ensure_slash_after_tld(url) for url in target_urls]}]
    return post_request("backlinks/bulk_backlinks/live", json_payload)


def get_serp_google_organic_live_advanced(keywords: str) -> ApiResponse:
    json_payload = [
        {
            "keyword": keywords,
            "location_code": 2840,  # United States
            "language_code": "en",
            "device": "desktop",  # or "mobile"
            "os": "macos",
            "depth": 100,
            # search engine parameters like "&tbs=qdr:h"
        }
    ]
    return post_request("serp/google/organic/live/advanced", json_payload)


# TODO: Learn how to use this API, so far it is return no results
# https://docs.dataforseo.com/v3/dataforseo_labs/google/competitors_domain/live/?python
def labs_competitors_domain(target_url: str) -> ApiResponse:
    json_payload = [
        {
            "target": ensure_slash_after_tld(target_url),
            "location_name": "United States",
            "language_name": "English",
            "exclude_top_domains": True,
            "filters": [
                [
                    ["metrics.organic.count", ">=", 5],  # was 50
                    "and",
                    [
                        "metrics.organic.pos_1",
                        "in",
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    ],  # was 1, 2, 3
                ],
                "or",
                ["metrics.organic.etv", ">=", 10],  # was 100
            ],
            "limit": 10,
        }
    ]
    # POST /v3/dataforseo_labs/google/competitors_domain/live
    return post_request("dataforseo_labs/google/competitors_domain/live", json_payload)


def get_result_items_safe(api_response: ApiResponse, expected_items_count: Optional[int] = None) -> list[dict]:
    # TODO(P2, devx): extraction of result items - make into a helper function
    assert (
            api_response.status_code == 20000
    ), f"un-expected api response status code: {api_response.status_code}: {api_response.status_message}"
    assert (
            api_response.tasks_error == 0
    ), f"tasks_error occurred: {api_response.tasks_error}"
    assert (
            api_response.tasks_count == 1
    ), f"tasks_count should be 1 it is: {api_response.tasks_count}"
    task = api_response.tasks[0]
    assert task.status_code, (
            20000
            == f"un-expected task status code: {task.status_code}: {task.status_message}"
    )
    # here I am unsure why result_count seems to always be 1 :/
    result = task.result[0]
    items_count = result.items_count
    if expected_items_count and items_count != expected_items_count:
        print(f"un-expected task.result.items_count {items_count} vs expected_items_count")
        # print(batch_jobs)

    return result.items


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


# TODO(P1, cost): This is somewhat expensive operation.
#   We should separate out the field updates and the OpenAI API calls.
if __name__ == "__main__":
    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        plugins = list(Plugin.select().where(Plugin.user_count > 1000).order_by(fn.COALESCE(Plugin.user_count, -1).desc()))
        print("Found plugins:", len(plugins))

    all_backlinks_count = json.load(open("batch_jobs/backlinks_data/backlinks-count-all.json"))
    assert isinstance(all_backlinks_count, dict) and len(all_backlinks_count.keys()) > 1000

    for i, plugin in enumerate(plugins):
        print(int(time.time()), i+1, plugin.name, plugin.marketplace_id, plugin.marketplace_link, plugin.developer_link, plugin.user_count)
        filepath_prefix = f"batch_jobs/backlinks_data/{plugin.marketplace_id}--"
        filepath_backlinks = filepath_prefix + "backlinks.json"
        filepath_competitors = filepath_prefix + "competitors.json"

        popular_enough = all_backlinks_count.get(plugin.marketplace_link, 0) > 20
        backlinks_items = None
        if popular_enough and plugin.marketplace_link:
            if not os.path.exists(filepath_backlinks):
                print("get_backlinks_backlinks_live for ", plugin.marketplace_link)
                backlinks_response = get_backlinks_backlinks_live(plugin.marketplace_link)
                backlinks_items = get_result_items_safe(backlinks_response)
                with open(filepath_backlinks, "w") as f:
                    json.dump(backlinks_items, f)
            # print(backlinks_items)
            else:
                backlinks_items = json.load(open(filepath_backlinks))

        enough_backlinks = backlinks_items and len(backlinks_items) > 50
        # About 20% of total* would get 0 competitors so sparing money here. *(not counting missing)
        # Therefore we only get competitors if there are enough backlinks
        if enough_backlinks and plugin.developer_link and not os.path.exists(filepath_competitors):
            developer_domain = urlparse(plugin.developer_link).netloc
            print("get_backlinks_competitors_live for ", developer_domain)
            # NOTE: For lower ranks (below like 20ish) the competitors are not very useful
            # BUT since most of the cost comes from the API call we just do it anyway lol
            competitors_response = get_backlinks_competitors_live(developer_domain, min_rank=5, limit=100)
            competitors_items = get_result_items_safe(competitors_response)
            with open(filepath_competitors, "w") as f:
                json.dump(competitors_items, f)
            print("Competitors count:", len(competitors_items) if competitors_items else "NO RESULTS")

        # TODO(P1, ux): Actually add it to the site / dataset (GPT summarize?)


# if __name__ == "__main__":
    # The backlinks API seems to work better than the labs one
    # print(get_backlinks_competitors_live("https://mailmeteor.com/"))
    # print(labs_competitors_domain("mailmeteor.com") or "No results")
