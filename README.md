# Django Betting Tracker

A sleek, modern web application for tracking your sports bets, viewing your dashboard, and analyzing your betting history.

## Features
- Track bets (stake, odds, status)
- Interactive Dashboard
- Profit / Loss Analytics
- User Authentication

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py migrate`
5. Run server: `python manage.py runserver`

## Demo credentials (local testing)

This project includes management commands to generate demo data (matches, outcomes, demo users) for local development.

- Generate random matches:

	`python manage.py generate_matches --count 10`

- Create demo users and write credentials to `demo_creds.txt`:

	`python manage.py create_demo_users --randomize-passwords --output-file demo_creds.txt --verify --bets 3`

	The command writes `demo_creds.txt` containing lines like `alice:random_password` and verifies the credentials by attempting to log in.

Security note: `demo_creds.txt` contains plaintext passwords and is intended only for local development. Do not commit it to source control or leave it on production machines. Delete it after testing or move credentials into a secure secrets manager.
