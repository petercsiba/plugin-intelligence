# Split the data by new lines and store it in a list
# Read the input file
import csv
import re

with open('scripts/localdata/ycombinator-input.txt', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()


# Function to extract job information from company block
def extract_job_info(block):
    if len(block) < 7:
        # This mostly happens when there are multiple job listings for the same company
        print("Invalid block: ", block)
        return {}

    company_name = block[0]
    description = block[1]
    website = block[2]
    employees = block[3]
    sector = block[4]
    job_title = block[5]

    # Extract salary, equity, experience info from the job listing line
    job_details = " ".join(block[6:])
    print(job_details)

    location_match = re.search(r'([A-Za-z\s,]+)(?:fulltime)', job_details)
    location = ''
    if location_match:
        location = location_match.group(1).strip()
    salary_match = re.search(r'\$(\d+K - \d+K)', job_details)
    salary = salary_match.group(1) if salary_match else ''
    equity_match = re.search(r'(\d+\.\d+% - \d+\.\d+%)', job_details)
    equity = equity_match.group(1) if equity_match else ''
    experience_match = re.search(r'(\d+\+ years)', job_details)
    experience = experience_match.group(1) if experience_match else ''

    return {
        'Company': company_name,
        'Description': description,
        'Website': website,
        'Employees': employees,
        'Sector': sector,
        'Job Title': job_title,
        'Location': location,
        'Salary': salary,
        'Equity': equity,
        'Experience': experience
    }


# Regex pattern to detect the start of a new company block
company_block_start_pattern = r"\([SW][1-2][0-9]\)"

# Iterate over lines and gather company blocks
parsed_jobs = []
block = []
for line in lines:
    # Detect start of a new block
    if re.search(company_block_start_pattern, line):
        if block:
            parsed_jobs.append(extract_job_info(block))
        block = [line]  # Start new block with company batch
    elif block:  # Continue adding lines to the current block
        block.append(line)

# Append the last block after iteration
if block:
    parsed_jobs.append(extract_job_info(block))

# Write the results to a CSV file
with open('scripts/localdata/ycombinator-output.csv', 'w', newline='') as csvfile:
    fieldnames = ['Company', 'Description', 'Website', 'Employees', 'Sector', 'Job Title', 'Location',
                  'Salary', 'Equity', 'Experience']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for job in parsed_jobs:
        writer.writerow(job)
