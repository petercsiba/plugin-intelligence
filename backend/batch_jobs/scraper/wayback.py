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


# This can take quite some time to fetch all snapshots
def _fetch_all_snapshots(target_url) -> List[WaybackSnapshot]:
    # The base URL for the CDX Server API
    cdx_url = 'https://web.archive.org/cdx/search/cdx'
    params = {
        'url': target_url,
        'output': 'json',
        'fl': 'timestamp,original'
    }

    print(f"Wayback: Fetching all snapshots for params {params}")
    with Timer("Wayback: Fetching all snapshots"):
        response = requests.get(cdx_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Skip the first item as it is the field names
            snapshots = [WaybackSnapshot(url=item[1], timestamp=item[0]) for item in data[1:]]
            print(data[1])
            return snapshots
        else:
            print("Wayback: Failed to fetch snapshots")
            return []


def wayback_get_all_snapshot_urls(target_url: str, day_step: int = 1) -> List[WaybackSnapshot]:
    if day_step < 1:
        raise ValueError(f"day_step must be at least 1, {day_step} given.")

    all_snapshots = _fetch_all_snapshots(target_url)
    filtered_snapshots = []
    last_date = None

    for snapshot in all_snapshots:
        snapshot_date = datetime.strptime(snapshot.timestamp[:8], '%Y%m%d')

        if last_date is None or snapshot_date >= last_date + timedelta(days=day_step):
            filtered_snapshots.append(snapshot)
            last_date = snapshot_date
        else:
            print("Wayback: Skipping snapshot due to day step", snapshot.timestamp)

    print(f"Wayback: Filtered {len(filtered_snapshots)} out of {len(all_snapshots)} snapshots.")
    return filtered_snapshots


# Documentation as of 2013:
# At this time, archived_snapshots just returns a single CLOSEST snapshot (before or after),
# but additional snapshots may be added in the future.
def wayback_get_closest_snapshot(target_url: str) -> Optional[WaybackSnapshot]:
    base_url = "https://archive.org/wayback/available"

    params = {"url": target_url}

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
        print(f"Wayback: Snapshot error status: {snapshot_info['status']} {snapshot_info}")
        return None

    # Create a WaybackSnapshot and add it to the list
    snapshot = WaybackSnapshot(
        url=snapshot_info["url"],
        timestamp=snapshot_info["timestamp"],
    )
    return snapshot


def main():
    # Usage example:
    test_url = "https://workspace.google.com/marketplace/app/pdf_viewer/619241882594"
    print(f"Closest snapshot for {wayback_get_closest_snapshot(test_url)}")

    snapshots = wayback_get_all_snapshot_urls(test_url)
    for snapshot in snapshots:
        print(f"Snapshot URL: {snapshot.url}, Timestamp: {snapshot.timestamp}")

    response = requests.get(snapshot.wayback_url())
    print(f"GET snapshot for {snapshot.wayback_url()} status_code: {response.status_code}")


if __name__ == "__main__":
    main()
