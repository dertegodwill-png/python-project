# Django Betting Tracker

A sleek, modern web application for tracking your sports bets, viewing your dashboard, and analyzing your betting history.

## Features

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py migrate`
5. Run server: `python manage.py runserver`

## Demo credentials (local testing)

This repository includes a `render.yaml` manifest that creates a web service and a managed Postgres on Render's free plan. To deploy quickly:

1. Sign in to https://render.com and connect your GitHub account.
2. In Render, go to Dashboard → New → Import from GitHub and pick `dertegodwill-png/python-project`.
3. Render will detect `render.yaml` and propose to create the web service and database. Confirm the resources.
4. In the new service's Environment settings, set:
	- SECRET_KEY = (paste a secure key generated locally)
	- DEBUG = False
	- ALLOWED_HOSTS = (the Render service URL)
5. Click Deploy. Render will run the build and start commands defined in `render.yaml`.

If you prefer to configure manually, use this build command instead:

```
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

And this start command:

```
gunicorn betting_tracker.wsgi:application --bind 0.0.0.0:$PORT
```

After deployment, open the service URL and run `createsuperuser` from the Render Shell to create an admin account.
	`python manage.py generate_matches --count 10`

- Create demo users and write credentials to `demo_creds.txt`:

	`python manage.py create_demo_users --randomize-passwords --output-file demo_creds.txt --verify --bets 3`

	The command writes `demo_creds.txt` containing lines like `alice:random_password` and verifies the credentials by attempting to log in.

Security note: `demo_creds.txt` contains plaintext passwords and is intended only for local development. Do not commit it to source control or leave it on production machines. Delete it after testing or move credentials into a secure secrets manager.
