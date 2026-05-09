#1 Imports
from flask import Flask, request, redirect, session, render_template
from datetime import datetime
import sqlite3
import bcrypt
import time
import os

app = Flask(__name__)
app.secret_key = "simplekey"

login_attempts = {}
LOCK_TIME = 60


#2 Setup databases (refreshes each run)
def init_db():

    if os.path.exists("book_database.db"):
        os.remove("book_database.db")

    if os.path.exists("usernames_pass_database.db"):
        os.remove("usernames_pass_database.db")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    # Books table
    cursor.execute("""
    CREATE TABLE books (
        title TEXT,
        author TEXT,
        copies INTEGER,
        genre TEXT
    )
    """)

    # Checkout table
    cursor.execute("""
    CREATE TABLE checkout (
        username TEXT,
        book TEXT
    )
    """)

    # Checkout log (timestamp tracking)
    cursor.execute("""
    CREATE TABLE checkout_log (
        username TEXT,
        book TEXT,
        checkout_time TEXT
    )
    """)

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

    # Users DB
    db = sqlite3.connect("usernames_pass_database.db")

    db.execute("""
    CREATE TABLE login(
        username TEXT PRIMARY KEY,
        passwords TEXT,
        role TEXT
    )
    """)

    db.execute("INSERT INTO login VALUES (?, ?, ?)",
        ("admin", bcrypt.hashpw("Admin123".encode(), bcrypt.gensalt()).decode(), "staff"))

    db.commit()
    db.close()


#3 Connect user DB
def connect_db():
    return sqlite3.connect("usernames_pass_database.db")


#4 Home
@app.route("/")
def home():
    return render_template("index.html")


#5 Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    if len(password) < 8:
        return render_template("register.html", error="Password must be 8+ characters, including uppercase, lowercase, and a number")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = connect_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO login VALUES (?, ?, ?)", (username, hashed, "user"))
        db.commit()
    except:
        return render_template("register.html", error="Username exists")

    db.close()
    return redirect("/")


#6 Login
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM login WHERE username=?", (username,))
    user = cursor.fetchone()
    db.close()

    if not user:
        return render_template("index.html", error="User not found")

    if not bcrypt.checkpw(password.encode(), user[1].encode()):
        return render_template("index.html", error="Wrong password")

    session["user"] = username
    session["role"] = user[2]

    return redirect("/dashboard")


#7 Forgot password
@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "GET":
        return render_template("forgot.html")

    username = request.form["username"]
    new_password = request.form["password"]

    if len(new_password) < 8:
        return render_template("forgot.html", error="Password must be 8+")

    db = connect_db()
    cursor = db.cursor()

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    cursor.execute("UPDATE login SET passwords=? WHERE username=?", (hashed, username))
    db.commit()
    db.close()

    return redirect("/")


#8 Dashboard 
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    search = request.args.get("search")

    if search:
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()

    cursor.execute("SELECT book FROM checkout WHERE username=?", (session["user"],))
    checked_books = [row[0] for row in cursor.fetchall()]

    db.close()

    return render_template("books.html", books=books, checked_books=checked_books)


#9 Checkout
@app.route("/checkout/<book>", methods=["POST"])
def checkout(book):

    if "user" not in session:
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("SELECT copies FROM books WHERE title=?", (book,))
    result = cursor.fetchone()

    if result and result[0] > 0:
        cursor.execute("UPDATE books SET copies = copies - 1 WHERE title=?", (book,))
        cursor.execute("INSERT INTO checkout VALUES (?, ?)", (session["user"], book))

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO checkout_log VALUES (?, ?, ?)",
            (session["user"], book, current_time)
        )

        db.commit()

    db.close()
    return redirect("/dashboard")


#10 Staff panel
@app.route("/staff")
def staff():

    if "user" not in session or session.get("role") != "staff":
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        b.title,
        b.author,
        b.copies,
        b.genre,
        GROUP_CONCAT(c.username),
        MAX(cl.checkout_time)
    FROM books b
    LEFT JOIN checkout c ON b.title = c.book
    LEFT JOIN checkout_log cl ON b.title = cl.book
    GROUP BY b.title
    """)

    records = cursor.fetchall()
    db.close()

    return render_template("admin.html", records=records)


#11 Add book
@app.route("/add_book", methods=["POST"])
def add_book():

    if "user" not in session or session.get("role") != "staff":
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO books VALUES (?, ?, ?, ?)",
        (request.form["title"], request.form["author"], request.form["copies"], request.form["genre"])
    )

    db.commit()
    db.close()

    return redirect("/staff")


#12 Delete book
@app.route("/delete_book/<title>")
def delete_book(title):

    if "user" not in session or session.get("role") != "staff":
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("DELETE FROM books WHERE title=?", (title,))
    cursor.execute("DELETE FROM checkout WHERE book=?", (title,))
    cursor.execute("DELETE FROM checkout_log WHERE book=?", (title,))

    db.commit()
    db.close()

    return redirect("/staff")


#13 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


#14 Run app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)