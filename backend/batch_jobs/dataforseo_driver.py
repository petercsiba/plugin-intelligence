# TODO Try competitor backlinks https://dataforseo.com/help-center/find-competitors-by-backlinks
# https://api.dataforseo.com/v3/dataforseo_labs/google/historical_bulk_traffic_estimation/live

import json
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, urlunparse

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

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
            "limit": 100,
            "internal_list_limit": 10,
            "offset": 0,
            "backlinks_status_type": "live",
            "include_subdomains": True,
            "mode": "as_is",
        }
    ]
    return post_request("backlinks/backlinks/live", json_payload)


def get_backlinks_bulk_backlinks_live(target_urls: list[str]) -> ApiResponse:
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


if __name__ == "__main__":
    # The backlinks API seems to work better than the labs one
    print(get_backlinks_competitors_live("https://mailmeteor.com/"))
    # print(labs_competitors_domain("mailmeteor.com") or "No results")
