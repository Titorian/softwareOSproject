#app.py:Fletcher 
from flask import Flask, request, redirect, session
import sqlite3
import re
import bcrypt
import time

app = Flask(__name__)
app.secret_key = "simplekey"

def connect_db():
    return sqlite3.connect("usernmaes_pass_database")


#pass validation
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


#login LockSYstem
login_attempts = {}
LOCK_TIME = 60  


#login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Invalid input"

    #lockFeature(Honors Credit)
    if username in login_attempts:
        attempts, last_attempt = login_attempts[username]

        if attempts >= 3 and time.time() - last_attempt < LOCK_TIME:
            return "Too many failed attempts. Try again later."

    db = connect_db()

    user = db.execute(
        "SELECT * FROM login WHERE username = ?",
        (username,)
    ).fetchone()

    if user:
        stored_password = user[1]

        login_success = False

        try:
            # Try bcrypt (if hashed)
            login_success = bcrypt.checkpw(
                password.encode(),
                stored_password.encode('utf-8')
            )
        except:
            login_success = (password == stored_password)

        if login_success:
            session["user"] = username
            session["role"] = "user"

            # reset attempts after 60sec time
            login_attempts[username] = (0, time.time())

            return redirect("/dashboard")

    #failedLogin
    attempts, _ = login_attempts.get(username, (0, 0))
    login_attempts[username] = (attempts + 1, time.time())

    return "Login failed"


#register
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Fields cannot be empty"

    if not is_strong_password(password):
        return "Password must be strong"

    #hashpassword
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    db = connect_db()

    try:
        db.execute(
            "INSERT INTO login (username, passwords) VALUES (?, ?)",
            (username, hashed_password)
        )
        db.commit()
    except:
        return "Username already exists"

    return redirect("/")


#dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return "Not logged in"

    return f"Welcome {session['user']}!"


#logout
@app.route("/logout")
def logout():
    session.clear()
    return "Logged out"


if __name__ == "__main__":
    app.run(debug=True)
