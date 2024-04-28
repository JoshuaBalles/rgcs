# app.py (do not change/remove this comment)

import os.path
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from models import db, User

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.secret_key = os.environ.get("SECRET_KEY")


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


def authenticate_user(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.password == password:
        return user
    else:
        return None


def validate_password(password, confirmpassword):
    if password != confirmpassword:
        flash("Passwords do not match. Please try again.", category="error")
        return False
    return True


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = authenticate_user(email, password)
    if user:
        return redirect(url_for("home"))
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

        if validate_password(password, confirmpassword):
            insert_user(firstname, lastname, email, password)
            return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/appointments")
def appointments():
    return render_template("appointments.html")


@app.route("/reviews")
def reviews():
    return render_template("reviews.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
