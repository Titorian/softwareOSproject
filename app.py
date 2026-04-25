#app.py:Fletcher 
from flask import Flask, request, redirect, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "simplekey"

def connect_db():
    return sqlite3.connect("usernmaes_pass_database")


#PASSWORD VALIDATION
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


#LOGIN
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Invalid input"

    db = connect_db()

    #MATCHES TEAM TABLE (login)
    user = db.execute(
        "SELECT * FROM login WHERE username = ?",
        (username,)
    ).fetchone()

    if user:
        stored_password = user[1]  # (username, passwords)

        #plain text comparison for now
        if password == stored_password:
            session["user"] = username
            session["role"] = "user"  # placeholder so dashboard works
            return redirect("/dashboard")

    return "Login failed"


#REGISTER
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Fields cannot be empty"

    if not is_strong_password(password):
        return "Password must be 8+ chars, include uppercase, lowercase, and number"

    db = connect_db()

    try:
        db.execute(
            "INSERT INTO login (username, passwords) VALUES (?, ?)",
            (username, password)
        )
        db.commit()
    except:
        return "Username already exists"

    return redirect("/")


#DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return "Not logged in"

    return f"Welcome {session['user']}!"


#LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return "Logged out"


if __name__ == "__main__":
    app.run(debug=True)
