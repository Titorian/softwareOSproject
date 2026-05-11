#1 Imports
from flask import Flask, request, redirect, session, render_template
from datetime import datetime
import sqlite3
import re
import bcrypt
import time
import os

app = Flask(__name__)
app.secret_key = "simplekey"

def connect_db():
    return sqlite3.connect("usernmaes_pass_database")

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
     # staff accounts
    staff_accounts = [
        ("admin",   "Admin123"),
    ]



    for username, password in staff_accounts:
        db.execute("INSERT INTO login VALUES (?, ?, ?)",
            (username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), "staff"))
        
       # regular user accounts
    user_accounts = [
        ("tim101",      "ilikecats22"),
        ("jon3",        "test12"),
        ("catwomen",    "iamcool10"),
        ("heyguys21",   "password4"),
        ("iluvreading", "doggo8")
    ]
    for username, password in user_accounts:
        db.execute("INSERT INTO login VALUES (?, ?, ?)",
            (username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), "user"))


    db.commit()
    db.close()


#3 Connect user DB
def connect_db():
    return sqlite3.connect("usernames_pass_database.db")


#4 Home
@app.route("/")
def home():
    return render_template("index.html")


    #failedLogin
    login_attempts[username] = (attempts + 1, time.time())


#can browse but can not checkout books
@app.route("/browse")
def browse():
    db = sqlite3.connect("book_database.db")  # ← fixed
    cursor = db.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
   

    db.close()

    return render_template("books.html", books=books)

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
    if user[2] == "staff":
        return redirect("/staff")   # ← librarian/admin goes here
    else:
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
#-----------------User Functions-------------------------------------------------
@app.route("/home")
def userhome():                  
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute(
        "SELECT book FROM checkout WHERE username = ?", 
        (username,)
    )
    checked_out = [row[0] for row in cursor.fetchall()]

    db.close()
    return render_template("userhome.html", username=username, checked_out=checked_out)


#allows user to return books
@app.route("/return/<book>", methods=["POST"])
def return_book(book):
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    db = sqlite3.connect("book_database.db")  # ← fixed, no connect_bookdb()
    cursor = db.cursor()

    cursor.execute("UPDATE books SET copies = copies + 1 WHERE title=?", (book,))  # ← title not titles
    cursor.execute(
        "DELETE FROM checkout WHERE username=? AND book=?",  # ← checkout not checkouts, book not title
        (username, book)
    )

    db.commit()
    db.close()
    return redirect("/home")





#8 Dashboard 
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()
    username = session["user"]

    search = request.args.get("search")

    if search:
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()
   

    cursor.execute("SELECT book FROM checkout WHERE username=?", (session["user"],))
    checked_books = [row[0] for row in cursor.fetchall()]

    db.close()

    return render_template("userbooks.html", books=books,username=username, checked_books=checked_books)


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
#--------------------------User Functions--------------------------------------------------------------




#---------------- Admin Stuff-----------------------------------------------------------------

#10 can check user accounts
@app.route("/accounts")
def accounts():

    if "user" not in session or session.get("role") != "staff":
        return redirect("/")

    db2 = connect_db()
    cursor2 = db2.cursor()
    cursor2.execute("SELECT * FROM login")
    logins = cursor2.fetchall()
    db2.close()

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()
    # pull from checkout_log so we get the timestamp too
    cursor.execute("SELECT username, book, checkout_time FROM checkout_log")
    checkouts = cursor.fetchall()
    db.close()

    return render_template("admin.html", logins=logins, checkouts=checkouts)

#can modify books
@app.route("/staff")
def staff():

    if "user" not in session or session.get("role") != "staff":
        return redirect("/")

    db = sqlite3.connect("book_database.db")
    cursor = db.cursor()

    cursor.execute("SELECT title, author, copies, genre FROM books")

    records = cursor.fetchall()
    db.close()

    return render_template("modifylib.html", records=records)


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
