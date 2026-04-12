#app.py:Fletcher 
from flask import Flask, request, redirect, session
import sqlite3
import bcrypt

#first create app
app = Flask(__name__)

#logged in (sessions)
app.secret_key = "simplekey"


#connects to TJ's code
def connect_db():

    return sqlite3.connect("library.db")


#log in
@app.route("/login", methods=["POST"])
def login():

    #retrieves the input data of user such as their chosem username and password
    username = request.form["username"]
    password = request.form["password"]

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
    password = request.form["password"]

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

    #check if user is logged in
    if "user" not in session:
        return "Not logged in"

    #check role either librarian and User
    if session["role"] == "librarian":
        return "Librarian access granted"
    else:
        return "User access granted"



@app.route("/logout")
def logout():

    #log out
    session.clear()

    return "Logged out"



app.run(debug=True)
