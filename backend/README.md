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
pyenv virtualenv 3.9.16 plugin-intelligence
pyenv activate plugin-intelligence
pip install -r batch/batch_jobs.txt 
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

### Committing Changes
We use `pre-commit` to run flake8, isort, black.
BEWARE: Sometimes `black` and `isort` disagree. Then:
* Run `pre-commit run --all-files` - this runs it clean without stash / unstash.
* If it passes, run `git status`. Likely the problem files aren't stage for commit (or have unstaged changes).
You might want to default to always do `-a` for `git commit`.

Below is pretty much filtered https://supabase.com/docs/guides/getting-started/local-development#database-migrations
### Migrations: Create New Table
There are a few ways, the best feels like:
* Create a new table in Supabase UI: http://localhost:54323/project/default/editor
Get the SQL table definition of it from the UI
* MAKE SURE it has RLS enabled, otherwise the new table has public access through PostREST (yeah :/).
  * Easiest with `ALTER TABLE your_table_name ENABLE ROW LEVEL SECURITY;` (alternatively with their UI)
  * Note that if the RLS policy is empty, then backend can still query it either via Service KEY or directly DB password.
* Add non-trivial stuff (like multicolumn indexes)
```shell
# Navigate to ./backend
supabase migration new your_migration_name
# and copy paste the SQL migration to definition to the generated file

# generate new python models, add some functionality (might need chmod +x)
./database/generate_models.sh

# apply migrations - weird name i know, this takes quite long :/
# supabase db reset # OG way
supabase migration up

# (optional): To take a snapshot of your current local data, you want to dump your DB data into `seed.sql`
export PGPASSWORD=postgres; pg_dump -h localhost -p 54322 -U postgres -d postgres --schema=public -F p --inserts > supabase/seed.sql

# Make sure the new schema works

# Then push migrations to be applied in prod (the Peewee models would mostly work^TM)
supabase db push
```