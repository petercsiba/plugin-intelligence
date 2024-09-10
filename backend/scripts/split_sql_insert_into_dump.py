import os
import re
import subprocess

from dotenv import load_dotenv
from supawee.client import _get_postgres_kwargs


def split_sql_insert(input_file: str, batch_size=1000):
    with open(input_file, 'r') as f:
        # Read the first line to get the INSERT INTO statement
        first_line = f.readline().strip()

        # Extract the table name (including schema) and column names
        import re
        match = re.search(r'INSERT INTO "([^"]+)"."([^"]+)"\s*\(([^)]+)\)\s*VALUES', first_line)
        if not match:
            raise ValueError("Could not find INSERT INTO statement")

        schema_name = match.group(1)
        table_name = match.group(2)
        columns = match.group(3)

        # Process the rest of the file
        values = []
        current_value = []
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith('(') and re.match(r'\(\d+', stripped_line):
                if current_value:
                    values.append(''.join(current_value).strip().rstrip(','))
                current_value = [stripped_line]
            else:
                current_value.append(line)

        # Add the last value set
        if current_value:
            values.append(''.join(current_value).strip().rstrip(','))

    # Split values into batches
    # NOTE: We do from range 1 cause the first line is the columns names.
    batches = [values[i:i + batch_size] for i in range(1, len(values), batch_size)]

    output_dir = f"/Users/petercsiba/Downloads/{schema_name}.{table_name}"
    print("Will write output batches to", output_dir)
    if os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' already exists")
    else:
        os.mkdir(output_dir)

    # Write each batch to a separate file
    for i, batch in enumerate(batches, 1):
        output_file = f"{output_dir}/batch_{i}.sql"
        with open(output_file, 'w') as f:
            # We only do table name here as somehow for "public"."plugin" it yields
            # ERROR:  relation "public.plugin" does not exist
            f.write(f'INSERT INTO "{table_name}" ({columns}) VALUES\n')
            f.write(',\n'.join(batch))
            f.write(';\n')

    print(f"Split into {len(batches)} files.")
    return output_dir


def load_to_supabase(dir_with_batches: str):
    load_dotenv()
    YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
        "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
    )
    params = _get_postgres_kwargs(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL)
    host = params["host"]
    port = params["port"]
    username = params["user"]
    database = params["database"]
    password = params["password"]

    print(f"Connecting to {host}:{port} as {username} to {database}")

    env = os.environ.copy()
    print("PGPASSWORD env variable is set to the .env param YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL.")
    env["PGPASSWORD"] = password

    # Load the batches to Supabase
    file_paths = sorted(os.listdir(dir_with_batches))
    for i, file_path in enumerate(file_paths):
        print(f"Loading file {i+1}/{len(file_paths)} {file_path}")
        file_path = os.path.join(dir_with_batches, file_path)
        subprocess.run(
            f"psql -h {host} -p {port} -U {username} -d {database} < {file_path}",
            shell=True,
            env=env,
        )


def main():
    for i in range(2, 13):
        input_file = f'/Users/petercsiba/Downloads/split_file{i}.sql'
        batch_size = 1000

        dir_with_batches = split_sql_insert(input_file, batch_size)
        load_to_supabase(dir_with_batches)


main()
