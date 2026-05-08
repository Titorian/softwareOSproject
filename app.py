from flask import Flask, request, redirect, session, render_template
import sqlite3
import bcrypt
import datetime
import time

app = Flask(__name__)
app.secret_key = "simplekey"

# Login Lock System
login_attempts = {}
LOCK_TIME = 60

# Book Database
def init_db():
    import os

    # reset database every time app starts
    if os.path.exists("book_database.db"):
        os.remove("book_database.db")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        title TEXT,
        author TEXT,
        copies INTEGER,
        genre TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login (
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkout (
        username TEXT,
        book TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkout_log (
        username TEXT,
        book TEXT,
        timestamp TEXT
    )
    """)

    # insert books
    books = [
        ("Shadow of the Moon", "Lena Carter", 12, "Fantasy"),
        ("Digital Fortress", "Aaron Blake", 5, "Thriller"),
        ("The Last Algorithm", "Maya Singh", 8, "Sci-Fi"),
        ("Echoes of War", "Daniel Hayes", 3, "Historical Fiction"),
        ("Mind Over Matter", "Sophia Reed", 10, "Self-Help"),
        ("The Silent Forest", "Ethan Cole", 6, "Mystery"),
        ("Quantum Dreams", "Noah Bennett", 4, "Science Fiction"),
        ("Broken Chains", "Ava Morales", 7, "Drama"),
        ("Cooking with Fire", "Gordon Hale", 15, "Cooking"),
        ("The Art of Focus", "Liam Brooks", 9, "Productivity"),
        ("Ocean Depths", "Isabella Cruz", 2, "Adventure"),
        ("Hidden Truths", "Oliver Grant", 11, "Crime")
    ]

    cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?)", books)

    db.commit()
    db.close()

# User Database
def connect_db():
    return sqlite3.connect("usernames_pass_database.db")

def init_db():
    db = connect_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS login(
        username TEXT PRIMARY KEY,
        passwords TEXT,
        role TEXT
    )
    """)

    # reset users every run
    db.execute("DELETE FROM login")
    db.commit()

    db.execute("INSERT INTO login VALUES (?, ?, ?)",
        ("testuser", bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode(), "user"))

    db.execute("INSERT INTO login VALUES (?, ?, ?)",
        ("admin", bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(), "admin"))

    db.commit()
    db.close()

init_db()

# Home
@app.route("/")
def home():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return render_template("register.html", error="Fields cannot be empty")

    # PASSWORD VALIDATION (THIS IS THE FIX)
    if len(password) < 8:
        return render_template("register.html",
            error="Password must be at least 8 characters, including an uppercase, lowercase, and number"
)
    if not any(c.isupper() for c in password):
        return render_template("register.html",
            error="Password must include an uppercase letter")

    if not any(c.islower() for c in password):
        return render_template("register.html",
            error="Password must include a lowercase letter")

    if not any(c.isdigit() for c in password):
        return render_template("register.html",
            error="Password must include a number")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = connect_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO login VALUES (?, ?, ?)", (username, hashed, "user"))
        db.commit()
    except:
        return render_template("register.html", error="Username already exists")

    db.close()
    return redirect("/")

# Forgot Password
@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "GET":
        return render_template("forgot.html")

    username = request.form["username"]
    new_password = request.form["password"]

    if not username or not new_password:
        return render_template("forgot.html", error="Fill all fields")

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM login WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        db.close()
        return render_template("forgot.html", error="User not found")

    cursor.execute("UPDATE login SET passwords=? WHERE username=?", (hashed, username))
    db.commit()
    db.close()

    return render_template("index.html", error="Password reset successful")

# Login
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    # lock check BEFORE hitting DB
    if username in login_attempts:
        attempts, last_time = login_attempts[username]

        if attempts >= 3 and (time.time() - last_time < LOCK_TIME):
            return render_template("index.html",
                error="Too many failed attempts. Try again in 1 minute or use Forgot Password.")

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM login WHERE username=?", (username,))
    user = cursor.fetchone()
    db.close()

    if not user:
        return render_template("index.html", error="User not found")

    # WRONG PASSWORD LOGIC (THIS IS THE FIX)
    if not bcrypt.checkpw(password.encode(), user[1].encode()):

        if username in login_attempts:
            attempts, last_time = login_attempts[username]
            login_attempts[username] = (attempts + 1, time.time())
        else:
            login_attempts[username] = (1, time.time())

        # LOCK TRIGGER AFTER 3
        if login_attempts[username][0] >= 3:
            return render_template("index.html",
                error="Too many failed attempts. Try again in 1 minute or use Forgot Password.")

        return render_template("index.html", error="Incorrect password")

    # SUCCESS → RESET ATTEMPTS
    login_attempts.pop(username, None)

    session["user"] = username
    session["role"] = user[2]

    return redirect("/dashboard")

# Dashboard with search
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return "Not logged in"

    search = request.args.get("search")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    if search:
        cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()

    cursor.execute("SELECT book FROM checkout WHERE username=?", (session["user"],))
    checked_out = [row[0] for row in cursor.fetchall()]

    db.close()

    return render_template("books.html", books=books, checked_out=checked_out)

# Checkout
@app.route("/checkout/<book>", methods=["POST"])
def checkout(book):

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("SELECT copies FROM books WHERE title=?", (book,))
    result = cursor.fetchone()

    if result and result[0] > 0:
        cursor.execute("UPDATE books SET copies = copies - 1 WHERE title=?", (book,))
        cursor.execute("INSERT INTO checkout VALUES (?, ?)", (session["user"], book))
        cursor.execute("INSERT INTO checkout_log VALUES (?, ?, ?)",
        (session["user"], book, str(datetime.datetime.now())))
        db.commit()

    db.close()
    return redirect("/dashboard")

# Return
@app.route("/return/<book>", methods=["POST"])
def return_book(book):

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("DELETE FROM checkout WHERE username=? AND book=?", (session["user"], book))
    cursor.execute("UPDATE books SET copies = copies + 1 WHERE title=?", (book,))

    db.commit()
    db.close()

    return redirect("/dashboard")

# Admin
@app.route("/admin")
def admin():

    if "user" not in session or session.get("role") != "admin":
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("""
        SELECT b.title, b.author, b.copies, b.genre,
        GROUP_CONCAT(c.username)
        FROM books b
        LEFT JOIN checkout c ON b.title = c.book
        GROUP BY b.title
    """)

    records = cursor.fetchall()
    db.close()

    return render_template("admin.html", records=records)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
