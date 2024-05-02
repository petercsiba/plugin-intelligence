import csv

# TODO: Add assistants API to estimate Revenue

# Define the condition to match in any column
# match_strings = ["95804724197", "887187948180", "922376225939", "1009043385982"]
match_strings = ["400312729360", "197076597243"]

# Open the CSV file
with open("batch_jobs/data/output-2024-04-28-19-09-06.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)  # Extract headers

    # Iterate over each row in the CSV
    for row in reader:
        for match_string in match_strings:
            if any(match_string in field for field in row):
                # Print column name and value if match_string is found in any field
                for header, field in zip(headers, row):
                    if header == "permissions":
                        continue
                    print(f"{header}: {field}")
