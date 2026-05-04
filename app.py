#app.py:Fletcher 
from flask import Flask, request, redirect, session, render_template
import sqlite3
import bcrypt
import re
from bookdata import Books, createbook, get_connection, get_books
from database import Accounts, get_connection2, passwordtohash

#-------Login Database--------------------------------------------------
conn2 = get_connection2()
cursor2 = conn2.cursor()
cursor2.execute("""CREATE TABLE IF NOT EXISTS
login(username TEXT PRIMARY KEY, passwords TEXT)""")

#adding to table
logins=[
    Accounts("tim101", passwordtohash("ilikecats22")),
    Accounts("jon3", passwordtohash("test12")),
    Accounts("dr.doom", passwordtohash("boomboom34")),
    Accounts("catwomen", passwordtohash("iamcool10")),
    Accounts("heyguys21", passwordtohash("password4")),
    Accounts("iluvreading", passwordtohash("doggo8"))
]

for login in logins:
    cursor2.execute(
        "INSERT OR IGNORE INTO login (username, passwords) VALUES (?, ?)",
        (login.username, login.password)
    )


# cursor2.execute("INSERT OR IGNORE INTO login (username, passwords) VALUES (?, ?)",("tim101", passwordtohash('ilikecats22')))
# cursor2.execute("INSERT OR IGNORE INTO login (username,passwords) VALUES (?,?)", ('jon3', passwordtohash('test12')))
# cursor2.execute("INSERT OR IGNORE INTO login (username,passwords) VALUES (?,?)",('dr.doom', passwordtohash('boomboom34')))
# cursor2.execute("INSERT OR IGNORE INTO login (username,passwords) VALUES (?,?)", ('catwomen', passwordtohash('iamcool10')))
# cursor2.execute("INSERT OR IGNORE INTO login (username,passwords) VALUES (?,?)", ('heyguys21', passwordtohash('password4')))
# cursor2.execute("INSERT OR IGNORE INTO login (username,passwords) VALUES (?,?)", ('iluvreading', passwordtohash('doggo8')))

conn2.commit()
conn2.close()
#------------------------------------------------------------------------

#///////////////// BOOKS Creation //////////////////////////////////

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    titles TEXT PRIMARY KEY,
    author TEXT,
    copies INT,
    genre TEXT
)
""")

books = [
    Books("Shadow of the Moon", "Lena Carter", 12, "Fantasy"),
    Books("Digital Fortress", "Aaron Blake", 5, "Thriller"),
    Books("The Last Algorithm", "Maya Singh", 8, "Sci-Fi"),
    Books("Echoes of War", "Daniel Hayes", 3, "Historical Fiction"),
    Books("Mind Over Matter", "Sophia Reed", 10, "Self-Help"),
    Books("The Silent Forest", "Ethan Cole", 6, "Mystery"),
    Books("Quantum Dreams", "Noah Bennett", 4, "Science Fiction"),
    Books("Broken Chains", "Ava Morales", 7, "Drama"),
    Books("Cooking with Fire", "Gordon Hale", 15, "Cooking"),
    Books("The Art of Focus", "Liam Brooks", 9, "Productivity"),
    Books("Ocean Depths", "Isabella Cruz", 2, "Adventure"),
    Books("Hidden Truths", "Oliver Grant", 11, "Crime")
]


for book in books:
    cursor.execute(
        "INSERT OR IGNORE INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)",
        (book.title, book.author, book.copies, book.genre)
    )


conn.commit()
conn.close()

#///////////////////BOOKS Creation//////////////////////////////////////////////
#first create app
app = Flask(__name__)

#logged in (sessions)
app.secret_key = "simplekey"


#connects to TJ's code
def connect_db():
    return sqlite3.connect("usernmaes_pass_database")
def connect_bookdb():
    return sqlite3.connect("book_database")


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

    #user input
    username = request.form["username"]
    password = request.form["passwords"]

    #hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    #connect to TJ's code
    db = connect_db()

    #new user in database
    db.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed_password, "user")  # default role = user
    )

    #save
    db.commit()

    #user back to login page
    return redirect("/")

#user account screens only the librarian can see
@app.route("/accounts")
def accounts():
    
    db2 = connect_db()
    cursor2 = db2.cursor()

    cursor2.execute("SELECT * FROM login")
    logins = cursor2.fetchall()
   # print(logins)
    db2.close()
    return render_template("logins.html", logins=logins)


#dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return "Not logged in"

    db = connect_bookdb()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if session["role"] == "librarian":
        return "Librarian access granted"
    else:
        return "User access granted"
    

    db.close()

    return render_template("books.html", books=books)


@app.route("/logout")
def logout():

    #log out
    session.clear()

    return "Logged out"



app.run(debug=True)
