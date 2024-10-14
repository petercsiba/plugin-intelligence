import re
import csv

# Your raw data as a string
with open('scripts/localdata/angellist-input.txt', 'r', encoding='utf-8') as f:
    data = f.read()


# Split data into blocks for each company
blocks = re.split(r'(?<=company logo)\n', data.strip())

jobs = []
for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) < 5:
        continue  # Skip incomplete blocks

    # Parse company info
    company_name = lines[0].replace('company logo', '').strip()
    company_status = lines[1].strip()
    company_desc_line = lines[2].strip()

    # Extract company description and number of employees
    company_desc_match = re.match(r'(.+?)(\d+-\d+ Employees)$', company_desc_line)
    if company_desc_match:
        company_desc = company_desc_match.group(1)
        num_employees = company_desc_match.group(2)
    else:
        company_desc = company_desc_line
        num_employees = ''
    idx = 3

    # Additional company info
    additional_info_lines = []
    while idx < len(lines) and not re.match(r'.*(Engineer|Manager)$', lines[idx].strip()):
        additional_info_lines.append(lines[idx].strip())
        idx += 1
    additional_company_info = '; '.join(filter(None, additional_info_lines))

    # Parse job postings
    while idx < len(lines):
        job_title = lines[idx].strip()
        idx += 1
        if idx < len(lines):
            location_work_salary_line = lines[idx].strip()
            idx += 1
        else:
            location_work_salary_line = ''
        if idx < len(lines):
            additional_job_info = lines[idx].strip()
            idx += 1
        else:
            additional_job_info = ''

        # Extract location, work type, salary, and equity
        location_match = re.match(r'([A-Za-z ,;/]+)(In office|Remote)', location_work_salary_line)
        if location_match:
            location = location_match.group(1).strip('; ')
            work_type = location_match.group(2)
        else:
            location = ''
            work_type = ''
        salary_match = re.search(r'\$\d+k – \$\d+k', location_work_salary_line)
        salary = salary_match.group(0) if salary_match else ''
        equity_match = re.search(r'• ([\d\.% –]+)', location_work_salary_line)
        if equity_match:
            equity = equity_match.group(1)
        elif '• No equity' in location_work_salary_line:
            equity = 'No equity'
        else:
            equity = ''

        # Clean additional job info
        additional_job_info = additional_job_info.replace('Recruiter recently active', 'Recruiter recently active; ').replace('Posted', 'Posted ')

        job = {
            'Company Name': company_name,
            'Company Status': company_status,
            'Company Description': company_desc,
            'Number of Employees': num_employees,
            'Additional Company Info': additional_company_info,
            'Job Title': job_title,
            'Location': location,
            'Work Type': work_type,
            'Salary': salary,
            'Equity': equity,
            'Additional Job Info': additional_job_info
        }
        jobs.append(job)
        # Only process first job per company for now
        break


# Write to CSV
with open('scripts/localdata/angellist-output.csv', 'w', newline='') as csvfile:
    fieldnames = ['Company Name', 'Company Status', 'Company Description', 'Number of Employees',
                  'Additional Company Info', 'Job Title', 'Location', 'Work Type', 'Salary', 'Equity', 'Additional Job Info']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for job in jobs:
        writer.writerow(job)
