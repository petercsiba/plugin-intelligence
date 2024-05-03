# Use an official lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app/backend

# `git` is required by python package `supawee`
# `postgresql-dev` and `libffi-dev` are for psycopg[binary,pool] (this is always such a pain to install)
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/

# Install Python dependencies
COPY requirements/batch_jobs.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary Python files and configurations
COPY __init__.py /app/backend
COPY config.py /app/backend
COPY pyproject.toml /app/backend
COPY setup.cfg /app/backend
# COPY backend/api backend/api
COPY batch_jobs /app/backend/batch_jobs
# We omit supabase/config.toml, supabase/seed.sql and migrations to be sure
COPY supabase/__init__.py /app/backend/supabase/
COPY supabase/models /app/backend/supabase/models/

# Environment variables are managed in two ways:
# * .env file for local
# * classic environmental variables (e.g. through fly.io secrets)

# Set the default command to execute
CMD ["python", "-m", "batch_jobs.google_workspace"]
