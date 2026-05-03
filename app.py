#app.py:Fletcher 
from flask import Flask, request, redirect, session, render_template
import sqlite3
import bcrypt
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


#log in
@app.route("/login", methods=["POST"])
def login():

    #retrieves the input data of user such as their chosem username and password
    username = request.form["username"]
    password = request.form["passwords"]

    #connects to TJ's code
    db = connect_db()

    #retrieves user from database by their username
    #"?" is used to prevent SQL injection
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    #checks if user is availible
    if user:

        #retrieves hashed password from database
        stored_password = user[2]

        #compares user input password to their hashed password
        if bcrypt.checkpw(password.encode(), stored_password):

            #saves user info keeping them logged in
            session["user"] = username
            session["role"] = user[3]

            #dashboard after login
            return redirect("/dashboard")


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
    print(logins)
    db2.close()
    return render_template("logins.html", logins=logins)


#dashboard
@app.route("/dashboard")
def dashboard():

    # if "user" not in session:
    #     return "Not logged in"

    db = connect_bookdb()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    

    db.close()

    return render_template("books.html", books=books)


@app.route("/logout")
def logout():

    #log out
    session.clear()

    return "Logged out"



app.run(debug=True)
