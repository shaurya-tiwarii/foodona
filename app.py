from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
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
    if con.execute("SELECT COUNT(*) FROM ngos").fetchone()[0] == 0:
        con.executemany("INSERT INTO ngos(name,address,phone) VALUES(?,?,?)", [
            ("Helping Hands NGO","Navi Mumbai","+91 9000000001"),
            ("Food For All Foundation","Mumbai","+91 9000000002"),
            ("Hope Community Centre","Panvel","+91 9000000003")
        ])
    con.commit(); con.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name=request.form["name"].strip(); email=request.form["email"].strip().lower()
        pw=request.form["password"]; role=request.form["role"]
        con=db()
        try:
            cur=con.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                            (name,email,generate_password_hash(pw),role))
            con.commit()
            session["user_id"]=cur.lastrowid; session["name"]=name; session["role"]=role
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("Email already registered.")
        finally: con.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        con=db(); u=con.execute("SELECT * FROM users WHERE email=?",(request.form["email"].lower(),)).fetchone()
        con.close()
        if u and check_password_hash(u["password"],request.form["password"]):
            session.update(user_id=u["id"],name=u["name"],role=u["role"])
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    con=db()
    ngos=con.execute("SELECT * FROM ngos").fetchall()
    if session["role"]=="Donor":
        donations=con.execute("""SELECT d.*,n.name ngo_name FROM donations d
            LEFT JOIN ngos n ON n.id=d.ngo_id WHERE d.donor_id=? ORDER BY d.id DESC""",(session["user_id"],)).fetchall()
    else:
        donations=con.execute("""SELECT d.*,u.name donor_name,n.name ngo_name FROM donations d
            JOIN users u ON u.id=d.donor_id LEFT JOIN ngos n ON n.id=d.ngo_id
            WHERE d.recipient_id=? OR d.status='Pending' ORDER BY d.id DESC""",(session["user_id"],)).fetchall()
    con.close()
    return render_template("dashboard.html",donations=donations,ngos=ngos)

@app.route("/donate",methods=["POST"])
def donate():
    if "user_id" not in session or session["role"]!="Donor": return redirect(url_for("login"))
    con=db(); con.execute("INSERT INTO donations(donor_id,ngo_id,food_name,quantity) VALUES(?,?,?,?)",
        (session["user_id"],request.form["ngo_id"],request.form["food_name"],request.form["quantity"]))
    con.commit(); con.close(); flash("Donation submitted.")
    return redirect(url_for("dashboard"))

@app.route("/accept/<int:donation_id>",methods=["POST"])
def accept(donation_id):
    if "user_id" not in session or session["role"]!="Recipient": return redirect(url_for("login"))
    con=db(); con.execute("UPDATE donations SET recipient_id=?,status='Accepted' WHERE id=? AND status='Pending'",
        (session["user_id"],donation_id)); con.commit(); con.close()
    flash("Donation accepted."); return redirect(url_for("dashboard"))

if __name__=="__main__":
    init_db(); app.run(debug=True)
