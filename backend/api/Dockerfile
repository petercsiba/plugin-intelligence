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
COPY requirements/api.txt /app/backend/requirements.txt
COPY requirements/common.txt /app/backend/common.txt
RUN pip install --no-cache-dir -r common.txt -r requirements.txt

# Copy only the necessary Python files and configurations
# TODO(P2, devx): rather use .dockerignore
COPY __init__.py /app/backend
COPY pyproject.toml /app/backend
COPY setup.cfg /app/backend
COPY api /app/backend/api
COPY common /app/backend/common
# We omit supabase/config.toml, supabase/seed.sql and migrations to be sure
COPY supabase/__init__.py /app/backend/supabase/
COPY supabase/models /app/backend/supabase/models/

# Environment variables are managed in two ways:
# * .env file for local
# * classic environmental variables (e.g. through fly.io secrets)

# NOTE: For larger apps gunicorn is suggested (we used that at my previous company)
# TODO: Remove --log-level debug
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]
