# TODO Try competitor backlinks https://dataforseo.com/help-center/find-competitors-by-backlinks

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
