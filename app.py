# app.py - do not remove this comment

import os
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    after_this_request,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure login manager with enhanced session protection
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "index"

# Unauthorized handler
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Please login first!", category="error")
    return redirect(url_for('index'))



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Authentication functions
def insert_user(firstname, lastname, email, password):
    existing_user = User.query.filter_by(email=email.lower()).first()
    if existing_user:
        flash("Email already exists. Please use a different email.", category="error")
        return False
    password_hash = generate_password_hash(password)
    new_user = User(
        firstname=firstname,
        lastname=lastname,
        email=email.lower(),
        password=password_hash,
    )
    db.session.add(new_user)
    db.session.commit()
    return True


def authenticate_user(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return user
    else:
        return None


def validate_password(password, confirmpassword):
    if password != confirmpassword:
        flash("Passwords do not match. Please try again.", category="error")
        return False
    return True


# Route definitions
@app.route("/")
@app.route("/login")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = authenticate_user(email, password)
    if user:
        return redirect(url_for("home"))
    else:
        flash("Invalid email or password.", category="error")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]
        confirmpassword = request.form["confirmpassword"]
        if validate_password(password, confirmpassword):
            if insert_user(firstname, lastname, email, password):
                flash("Successfully Signed Up!", category="success")
                return redirect(url_for("index"))
            else:
                return redirect(url_for("signup"))
    return render_template("signup.html")


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/services")
@login_required
def services():
    return render_template("services.html")


@app.route("/appointments")
@login_required
def appointments():
    return render_template("appointments.html")


@app.route("/reviews")
@login_required
def reviews():
    return render_template("reviews.html")


@app.after_request
def apply_caching(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
