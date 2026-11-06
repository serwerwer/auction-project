
# Auction platform

The aim of this project is to create a platform where the auction can take place.

## Local Development Setup

Follow these steps after cloning this repo for the first time.

1. Create and activate a virtual env: `python -m venv .venv`
2. Activate that environment
3. Install project dependencies from the requirements.txt file
4. Configure environment variables in .env file (based on .env.example), to do so generate your own Django secret key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### PostgreSQL - Local Setup

Each developer uses their own local PostgreSQL database running in Docker. Database credentials and data are not shared through Git. Before following the steps below make sure that your local .env file is set up.  

1. Install and start Docker Desktop.
2. Start PostgreSQL: `docker compose up -d db`
3. Check its status: `docker compose ps`

**!!! IMPORTANT Note:** Do not run database migrations until the custom `User` model has been added to the project !!!

### Django Admin - Local Setup

For now, each developer uses their own local database (SQLite) and administrator account. User credentials are not shared through Git, each developer maintains their own local database, admin account, and environment confuguration.

After pulling the latest changes:

1. Activate the Python virtual environment: `source .venv/Scripts/activate`
2. Apply database migrations: `python manage.py migrate`
3. Create a local administrator account (only required once): `python manage.py createsuperuser`
4. Start the development server: `python manage.py runserver`
5. Add "/admin" at the end of the server's URL and log in with your credentials you've just created.
