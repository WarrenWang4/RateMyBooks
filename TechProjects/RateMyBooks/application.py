import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# API key: t59leWaL2NACMvW9QrgoMg

@app.route("/", methods=["GET","POST"])
def index():
    """ Login user """

    # Forget any user_id
    session.clear()

    # Made sure request method is POST
    if request.method == "POST":

        # Assigning userInfo to the user's data 
        userInfo = db.execute("SELECT * FROM users WHERE email = :email", 
                        {"email":request.form.get("email")}).fetchone()

        # Checking if username and password is found in the database
        if userInfo and check_password_hash(userInfo[2], request.form.get("password")):

            return render_template("search.html")

        else:

            return render_template("error.html", message="invalid login credentials")

    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """
    
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Checks if users email is already in the database
        checkUser = db.execute("SELECT * FROM users WHERE email = :email", 
                        {"email":request.form.get("email")}).fetchone()

        if checkUser:
            return render_template("error.html", message="username already exists")

        #Checks if password confirmation matches password
        elif not request.form.get("password") == request.form.get("psw-repeat"):
            return render_template("error.html", message="passwords doesn't match")

        # Hash's user's password
        hashedPassword = generate_password_hash(request.form.get("password"), "sha256")

        # Store user's email and password in the database
        db.execute("INSERT INTO users (email, password) VALUES (:email, :password)",
            {"email": request.form.get("email"), "password": hashedPassword})

        db.commit()

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/search", methods=["GET"])
def search():
    """ Get books results """

    # Get the inputted book value by user
    searchedResult = request.args.get("book")

    # Assign myResults to any string containing searchedResults
    myResults = "%" + searchedResult + "%"

    # Selecting all the books that are like myResults
    resultData = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        title LIKE :myResults OR \
                        author LIKE :myResults",
                        {"myResults": myResults})

    # If there us none, return error message
    if resultData.rowcount == 0:
        return render_template("error.html", message="search results not found")

    results = resultData.fetchall()

    
    return render_template("results.html", results=results)









