#app.py:Fletcher 
from flask import Flask, request, redirect, session, render_template
import sqlite3
import bcrypt
from bookdata import Books, createbook, get_connection, get_books

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

#books
# book1  = Books("Shadow of the Moon", "Lena Carter", 12, "Fantasy")
# book2  = Books("Digital Fortress", "Aaron Blake", 5, "Thriller")
# book3  = Books("The Last Algorithm", "Maya Singh", 8, "Sci-Fi")
# book4  = Books("Echoes of War", "Daniel Hayes", 3, "Historical Fiction")
# book5  = Books("Mind Over Matter", "Sophia Reed", 10, "Self-Help")
# book6  = Books("The Silent Forest", "Ethan Cole", 6, "Mystery")
# book7  = Books("Quantum Dreams", "Noah Bennett", 4, "Science Fiction")
# book8  = Books("Broken Chains", "Ava Morales", 7, "Drama")
# book9  = Books("Cooking with Fire", "Gordon Hale", 15, "Cooking")
# book10 = Books("The Art of Focus", "Liam Brooks", 9, "Productivity")
# book11 = Books("Ocean Depths", "Isabella Cruz", 2, "Adventure")
# book12 = Books("Hidden Truths", "Oliver Grant", 11, "Crime")
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
