import time
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from pydantic import BaseModel

from common.utils import Timer


class WaybackSnapshot(BaseModel):
    url: str
    timestamp: str  # example: 20130919044612 or "20060101" (url param)

    def wayback_url(self):
        return f"https://web.archive.org/web/{self.timestamp}id_/{self.url}"

    def p_date(self) -> datetime.date:
        # Timestamp is in the form of 'YYYYMMDD'
        date_time = datetime.strptime(self.timestamp[:8], "%Y%m%d")
        return date_time.strftime("%Y-%m-%d")

    def p_date_str(self) -> datetime.date:
        return str(self.p_date())


# Web Archive has some rate limiting (likely 15/minute), so there is no need to speed this up using async.
# This also includes the WDX endpoint.
def requests_get_with_retry(
    url: str, params=None, retry_limit=3
) -> Optional[requests.Response]:
    retry_count = 0

    while retry_count < retry_limit:
        try:
            retry_count += 1
            # TODO(P1, devx): Since Wayback queries are so expensive (cause the rate limit),
            #   we store log the html content. Especially if we would to decide to re-parse it..
            return requests.get(url, params=params)
        # NOTE: requests.ConnectionError and NOT os.ConnectionError (or built-in ConnectionError)
        except requests.ConnectionError as e:
            sleep_time = (70 // 2) * 2**retry_count
            print(f"ConnectionError {e}")
            print(f"Sleeping {sleep_time} seconds and retrying {url}")
            time.sleep(sleep_time)

    return None


# This can take quite some time to fetch all snapshots
def _fetch_all_snapshots(target_url) -> List[WaybackSnapshot]:
    # The base URL for the CDX Server API
    cdx_url = "https://web.archive.org/cdx/search/cdx"
    params = {"url": target_url, "output": "json", "fl": "timestamp,original"}

    print(f"Wayback: Fetching all snapshots for params {params}")
    with Timer("Wayback: Fetching all snapshots"):
        response = requests_get_with_retry(cdx_url, params)
        if response and response.status_code == 200:
            data = response.json()
            # Skip the first item as it is the field names
            snapshots = [
                WaybackSnapshot(url=item[1], timestamp=item[0]) for item in data[1:]
            ]
            return snapshots
        else:
            print("Wayback: Failed to fetch snapshots")
            return []


def wayback_get_all_snapshot_urls(
    target_url: str, day_step: int = 1
) -> List[WaybackSnapshot]:
    if day_step < 1:
        raise ValueError(f"day_step must be at least 1, {day_step} given.")

    all_snapshots = _fetch_all_snapshots(target_url)
    filtered_snapshots = []
    last_date = None

    for snapshot in all_snapshots:
        snapshot_date = datetime.strptime(snapshot.timestamp[:8], "%Y%m%d")

        if last_date is None or snapshot_date >= last_date + timedelta(days=day_step):
            filtered_snapshots.append(snapshot)
            last_date = snapshot_date
        # else:
        #    print("Wayback: Skipping snapshot due to day step", snapshot.timestamp)

    print(
        f"Wayback: Returning {len(filtered_snapshots)} out of {len(all_snapshots)} snapshots for {target_url}."
    )
    return filtered_snapshots


# Documentation as of 2013:
# At this time, archived_snapshots just returns a single CLOSEST snapshot (before or after),
# but additional snapshots may be added in the future.
# `timestamp` is in the form of 'YYYYMMDDHHMMSS' or 'YYYYMMDD'
def wayback_get_closest_snapshot(
    target_url: str, timestamp: Optional[str] = None
) -> Optional[WaybackSnapshot]:
    base_url = "https://archive.org/wayback/available"

    params = {"url": target_url}
    if timestamp:
        params["timestamp"] = timestamp

    print(f"Wayback: Querying machine with params: {params}")
    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if a snapshot is available
    if not ("archived_snapshots" in data and "closest" in data["archived_snapshots"]):
        print(f"Wayback: No snapshots found in response, stopping. Data: {data}")
        return None

    snapshot_info = data["archived_snapshots"]["closest"]
    if not snapshot_info["available"]:
        print(f"Wayback: Snapshot not available {snapshot_info}")
        return None

    if snapshot_info["status"] != "200":
        print(
            f"Wayback: Snapshot error status: {snapshot_info['status']} {snapshot_info}"
        )
        return None

    # Create a WaybackSnapshot and add it to the list
    snapshot = WaybackSnapshot(
        url=snapshot_info["url"],
        timestamp=snapshot_info["timestamp"],
    )
    return snapshot


def main():
    # Usage example:
    # test_url_closest =
    # test_url_closest =
    # closest_snapshot = wayback_get_closest_snapshot(
    #   "https://workspace.google.com/marketplace/app/mailmeteor/1008170693301",
    #   timestamp="20231116"
    # )
    # print(f"Closest snapshot url {closest_snapshot.wayback_url()}")

    test_url_all = (
        "https://apps.google.com/marketplace/app/pipdgoflicmpcfocpejndfeegjmeokfh"
    )
    snapshots = wayback_get_all_snapshot_urls(test_url_all, day_step=30)
    for snapshot in snapshots:
        print(f"Snapshot URL: {snapshot.wayback_url()}")


if __name__ == "__main__":
    # closests = wayback_get_closest_snapshot(, )
    # print(closests)
    main()
