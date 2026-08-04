# FOODONA

A food donation web app I made with Flask. Donors post surplus food, recipients claim it, and everything is tracked from pending to delivered.

## What it does
- Register / login as a Donor or Recipient
- Donors create donations and assign an NGO
- Recipients see pending donations and accept them
- Donation status moves: Pending -> Accepted -> Collected -> Delivered

## How to run
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser.

The SQLite database (foodona.db) is created automatically on first run with 3 sample NGOs. Set the SECRET_KEY environment variable if you want to change the session key.

## Tech
Python, Flask, SQLite, plain HTML/CSS
