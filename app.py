from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# key used to sign session cookies
app.secret_key = os.environ.get("SECRET_KEY", "foodona-development-secret")
DB = os.path.join(os.path.dirname(__file__), "foodona.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('Donor','Recipient'))
    );
    CREATE TABLE IF NOT EXISTS ngos(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      address TEXT, phone TEXT
    );
    CREATE TABLE IF NOT EXISTS donations(
      id INTEGER PRIMARY KEY AUTOINCREMENT, donor_id INTEGER NOT NULL,
      recipient_id INTEGER, ngo_id INTEGER, food_name TEXT NOT NULL,
      quantity TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(donor_id) REFERENCES users(id),
      FOREIGN KEY(recipient_id) REFERENCES users(id),
      FOREIGN KEY(ngo_id) REFERENCES ngos(id)
    );
    """)
    con.commit(); con.close()

@app.route("/")
def index():
    return render_template("index.html")

if __name__=="__main__":
    init_db(); app.run(debug=True)
