# app.py (do not change/remove this comment)

import os.path
import sys
import logging
from flask import Flask, render_template, request, flash, redirect, url_for

# from flask_sqlalchemy import SQLAlchemy
from models import db, User

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

if not os.path.exists("secret_key.txt"):
    logging.error("Secret key found. Run config.py first.")
    sys.exit()
else:
    logging.info("Secret key and databases loaded successfully.")


# Function to load the secret key from file
def load_secret_key_from_file(filename):
    with open(filename, "r") as f:
        secret_key = f.read().strip()
    return secret_key


# Load the secret key from the generated file
SECRET_KEY_FILE = "secret_key.txt"
app.secret_key = load_secret_key_from_file(SECRET_KEY_FILE)


# Function to insert user into database
def insert_user(firstname, lastname, email, password):
    existing_user = User.query.filter_by(email=email.lower()).first()
    if existing_user:
        flash("Email already exists. Please use a different email.")
        return

    new_user = User(
        firstname=firstname, lastname=lastname, email=email.lower(), password=password
    )
    db.session.add(new_user)
    db.session.commit()


# Function to authenticate user
def authenticate_user(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.password == password:
        return user
    else:
        return None


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = authenticate_user(email, password)
    if user:
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid email or password. Please try again.")
        return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]
        confirmpassword = request.form["confirmpassword"]

        if password != confirmpassword:
            flash("Passwords do not match. Please try again.")
        else:
            insert_user(firstname, lastname, email, password)
            return redirect(url_for("index"))

    return render_template("signup.html")

@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
