import csv

# Define the field names based on your data structure
fields = [
    'company_logo', 'company_name', 'categories', 'description', 'number1',
    'date1', 'website', 'email', 'founders', 'number2', 'funding_amount',
    'funding_date', 'investors'
]

# Read the input file
with open('scripts/localdata/crunchbase-input.txt', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

# Find the indices where a new company record starts
company_indices = [i for i, line in enumerate(lines) if line.endswith('Logo')]
company_indices.append(len(lines))  # Add the end of the list to capture the last company

# Split the lines into records for each company
records = []
for idx in range(len(company_indices) - 1):
    start = company_indices[idx]
    end = company_indices[idx + 1]
    record_lines = lines[start:end]
    records.append(record_lines)

# Process each record and map it to the corresponding fields
records_data = []
for record in records:
    data = {}
    for i, field in enumerate(fields):
        if i < len(record):
            data[field] = record[i]
        else:
            data[field] = ''  # Fill missing fields with empty strings
    records_data.append(data)

# Write the data to a CSV file
with open('scripts/localdata/output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for data in records_data:
        writer.writerow(data)