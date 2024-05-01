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
pip install -r batch/requirements.txt 
```

If you using PyCharm like me make sure to update your project interpreter to the above virtualenv.


