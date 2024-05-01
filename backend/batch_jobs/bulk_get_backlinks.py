import csv
import os
import sys

from backend.batch_jobs.dataforseo_driver import ensure_slash_after_tld, get_backlinks_bulk_backlinks_live

# TODO(P1, cloud migration): Migrate to using database tables
# Check if two arguments are provided
if len(sys.argv) != 3:
    print("Usage: script.py input_csv_path output_csv_path")
    sys.exit(1)

# Assign the command line arguments to variables
INPUT_CSV_PATH = sys.argv[1]
OUTPUT_CSV_PATH = sys.argv[2]
TEMP_FILE = "temp.csv"


def get_backlinks_for(column_name: str, input_csv_path: str, output_csv_path: str):
    # Read the CSV file
    with open(input_csv_path, "r") as infile:
        reader = csv.DictReader(infile)
        rows = [row for row in reader]
        links = [ensure_slash_after_tld(row[column_name]) for row in rows]

    # Up to 1000 I believe, pricing is $0.02 + items * $0.00003 (so 1,000 items is $0.05)
    BATCH_SIZE = 1000
    # Batch links into groups of BATCH_SIZE and retrieve backlinks
    batched_links = [links[i : i + BATCH_SIZE] for i in range(0, len(links), BATCH_SIZE)]
    all_backlinks = {}
    for batch in batched_links:
        api_response = get_backlinks_bulk_backlinks_live(target_urls=batch)
        # TODO(P2, devx): extraction of result items - make into a helper function
        assert (
            api_response.status_code == 20000
        ), f"un-expected api response status code: {api_response.status_code}: {api_response.status_message}"
        assert api_response.tasks_error == 0, f"tasks_error occurred: {api_response.tasks_error}"
        assert api_response.tasks_count == 1, f"tasks_count should be 1 it is: {api_response.tasks_count}"
        task = api_response.tasks[0]
        assert task.status_code, 20000 == f"un-expected task status code: {task.status_code}: {task.status_message}"
        # here I am unsure why result_count seems to be 1 :/
        result = task.result[0]
        items_count = result.items_count
        if items_count != len(batch):
            print(f"un-expected task.result.items_count {items_count} vs {len(batch)}")
            # print(batch_jobs)

        backlinks = {item["target"]: item["backlinks"] for item in result.items}
        all_backlinks.update(backlinks)

    # Write to the new CSV file with the 'backlinks' column added
    with open(output_csv_path, "w", newline="") as outfile:
        original_fieldnames = reader.fieldnames
        link_index = original_fieldnames.index(column_name)
        new_column_name = f"{column_name}_backlinks"
        new_fieldnames = original_fieldnames[:link_index] + [new_column_name] + original_fieldnames[link_index:]

        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()
        for row in rows:
            link = ensure_slash_after_tld(row[column_name])
            row[new_column_name] = all_backlinks.get(link, "0")
            writer.writerow(row)


if __name__ == "__main__":
    get_backlinks_for("link", INPUT_CSV_PATH, TEMP_FILE)
    get_backlinks_for("developer_link", TEMP_FILE, OUTPUT_CSV_PATH)
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
