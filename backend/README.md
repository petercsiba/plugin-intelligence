# Plugin Intelligence Backend

Organized into two main parts:
* API: thin layer between frontend and database so serve requested data.
  * Yes, we could've used Supabase row-level security, BUT I like to have an abstraction layer in between.
* Batch Jobs: Workers ingesting data into our database.

## Stack
* Python
* Supabase for PostgresSQL
* Vercel for Python Flask Server Deployments

## Development

### Setup Python
```shell
# in the backend directory
pyenv virtualenv 3.12.2 plugin-intelligence
pyenv activate plugin-intelligence
make requirements

# for IDE like intelliJ, you would need to setup the VirtualEnv
echo "$VIRTUAL_ENV/python"
# Sth like /Users/petercsiba/.pyenv/versions/3.12.2/envs/plugin-intelligence/python
# Copy this into PyCharm -> Settings -> ... -> Python Interpreter -> Add Local Interpreter
```

### Setup Git
```shell
# setup pre-commit checks
pre-commit install --config .pre-commit-config.yaml
pre-commit run --all-files  # check if works
```

If you using PyCharm like me make sure to update your project interpreter to the above virtualenv.

### Setup Supabase
Pretty much a relevant summary of https://supabase.com/docs/guides/getting-started/local-development
The configuration will live in `backend/supabase` (part of .gitignore).

```shell
supabase init
# PLEASE do NOT store your DB password here - keep using chrome or Doppler.
supabase link --project-ref kubtuncgxkefdlzdnnue
# Get remote migrations
supabase db remote commit
# Start bunch of stuff (you will need Docker daemon / Colima start);
supabase start
```


## Development Workflow

### Running Tests
```shell
# For whatever reason, the tests are not running with the correct PYTHONPATH :/
# One day debug: https://chat.openai.com/share/1c47dfca-be7b-46f2-ad95-081d41346b18
PYTHONPATH=/Users/petercsiba/code/plugin-intelligence/backend pytest
```

### Committing Changes
We use `pre-commit` to run flake8, isort, black. Easiest to see results:
```shell
make lint-check  # optional for read-only mode
make lint  # actually modifies files
```
BEWARE: Sometimes `black` and `isort` disagree. Then:
* Run `pre-commit run --all-files` - this runs it clean without stash / unstash.
* If it passes, run `git status`. Likely the problem files aren't stage for commit (or have unstaged changes).
You might want to default to always do `-a` for `git commit`.

### Running Locally
```shell
uvicorn api.app:app --reload --port 8080
```

### Deploying Batch Jobs
To deploy API Server:
```shell
fly deploy --config api/fly.toml
```

To deploy daily scraper:
```shell
fly deploy --build_only --config batch_jobs/fly.toml --dockerfile batch_jobs/Dockerfile
```

To configure daily job:
```shell
# in /backend
fly machine run . --config batch_jobs/fly.toml --dockerfile batch_jobs/Dockerfile --schedule daily -a extension-scraper-daily
```

### Migrations: Create New Table
Most commands from https://supabase.com/docs/guides/getting-started/local-development#database-migrations

There are a few ways, the best feels like:
* Create a new table in Supabase UI: http://localhost:54323/project/default/editor
* Get the SQL table definition of it from the UI
* MAKE SURE it has RLS enabled, otherwise the new table has public access through PostREST (yeah :/).
  * Easiest with `ALTER TABLE your_table_name ENABLE ROW LEVEL SECURITY;` (alternatively with their UI)
  * Note that if the RLS policy is empty, then backend can still query it either via Service KEY or directly DB password.
* Add non-trivial stuff (like multicolumn indexes)
```shell
# Navigate to ./backend
supabase migration new your_migration_name
# and copy paste the SQL migration to definition to the generated file

# generate new python models
supawee supabase/models/base.py

# apply migrations - weird name i know, this takes quite long :/
# supabase db reset # OG way
supabase migration up

# (optional): To take a snapshot of your current local data, you want to dump your DB data into `seed.sql`
export PGPASSWORD=postgres; pg_dump -h localhost -p 54322 -U postgres -d postgres --schema=public -F p --inserts > supabase/seed.sql

# Make sure the new schema works

# Then push migrations to be applied in prod (the Peewee models would mostly work^TM)
supabase db push
```

### To test Dockerfile setup locally
```shell
docker build --no-cache -t extension-scraper-daily -f batch_jobs/Dockerfile .
# Will likely fail as I was lazy to setup DB config right for `localhost` vs `host.docker.internal`
docker run --env-file .env -p 4000:4000  extension-scraper-daily
```

### Create New Machine on Fly.io
```shell
# Do this and hit `Y` to update name and machine size / count
fly launch  && rm Procfile
# NOTE: Procfile is not needed as we deploy with Dockerfile
```

Then merge the generated `backend/fly.toml` into one of the existing ones scattered around the project.
Move it next to your Dockerfile. (one per directory)

If you gonna add secrets, or want to use a different database do sth like this:
```shell
fly secrets set "POSTGRES_DATABASE_URL=postgres://postgres.ngtdkctpkhzyqvkzshxk:<your-password>@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
```

To deploy it:
```shell
fly deploy --config batch_jobs/fly.toml
```

For batch jobs you might want to set restart policy to `no` so you can detect errors ASAP:
```shell
fly m update 9080ee4a653d08 --restart no
```

## Adding New Marketplaces
TODO: Extend this section with more details.

Just a few mind notes for now:
* Extend the `MarketplaceName` enum object
* Add a new timeseries table to DB for the new marketplace (see `google_workspace`)
* Write a scraper in `batch_jobs/scraper/new_marketplace_name.py`
* Run it locally until you confident it works well
* Add it to the `daily_scrape.py` and run it
* Add a translation from the timeseries object to the `Plugin` object in `upsert_plugins.py`
* Run it for all
* Now most backend work should be done
* Add a new `MarketplaceName` to the frontend
* Add a new route to `marketplaces/marketplace_name/page.tsx`
* You likely need to extend `nextConfig.images.domains` to allow 3rd party images through Next server
