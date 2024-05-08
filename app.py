# app.py - do not remove this comment
import logging
import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_mail import Mail, Message
from sqlalchemy import asc, desc
from werkzeug.security import check_password_hash, generate_password_hash

from models import Service, User, db

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Email configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("ADMIN_MAIL")
app.config["MAIL_PASSWORD"] = os.environ.get("ADMIN_TOKEN")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("ADMIN_MAIL")
mail = Mail(app)

# Configure login manager with enhanced session protection
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "index"


# Unauthorized handler
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Please login first!", category="error")
    return redirect(url_for("index"))


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
    send_registration_email(email, firstname)  # Send registration email
    return True


def send_registration_email(email, firstname):
    msg = Message(
        "Welcome to Our Service",
        sender=os.environ.get("ADMIN_MAIL"),
        recipients=[email],
    )
    msg.body = (
        f"Hi {firstname},\nWelcome to our service! We are glad to have you onboard."
    )
    mail.send(msg)


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
        # Redirect admin directly to admin page
        if current_user.email.lower() == os.environ.get("ADMIN_MAIL").lower():
            return redirect(url_for("admin"))
        return redirect(url_for("home"))
    return render_template("login.html", now=datetime.now())


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = authenticate_user(email, password)
    if user:
        # Redirect admin directly to admin page
        if email.lower() == os.environ.get("ADMIN_MAIL").lower():
            return redirect(url_for("admin"))
        return redirect(url_for("home"))
    else:
        flash("Invalid email or password.", category="error")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if request.method == "POST":
        return redirect(url_for("index"))
    return render_template("forgotpassword.html", now=datetime.now())


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
    return render_template("signup.html", now=datetime.now())


from flask import current_app


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if current_user.email.lower() == os.environ.get("ADMIN_MAIL").lower():
        return redirect(url_for("admin"))
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = current_user.email
        mobile_number = request.form["mobile_number"]
        street_address = request.form["street_address"]
        city = request.form["city"]
        room_size = request.form["room_size"]
        type_of_service = request.form["type_of_service"]
        addl_services = request.form.get("addl_services", "")
        selected_date = request.form["selected_date"]
        selected_time = request.form["selected_time"]

        new_service = Service(
            user_id=current_user.id,
            full_name=full_name,
            mobile_number=mobile_number,
            street_address=street_address,
            city=city,
            room_size=room_size,
            type_of_service=type_of_service,
            addl_services=addl_services,
            selected_date=selected_date,
            selected_time=selected_time,
        )
        db.session.add(new_service)
        db.session.commit()

        # Send email to admin
        admin_email = os.environ.get("ADMIN_MAIL").lower()
        subject = f"New Service Request for {selected_date}, {selected_time}"
        body = (
            f"Email: {email}\n"
            f"Full Name: {full_name}\n"
            f"Mobile Number: {mobile_number}\n"
            f"Street Address: {street_address}\n"
            f"City: {city}\n"
            f"Room Size: {room_size}\n"
            f"Type of Service: {type_of_service}\n"
            f"Additional Services: {addl_services}\n"
            f"Selected Date: {selected_date}\n"
            f"Selected Time: {selected_time}\n"
        )
        send_email(admin_email, subject, body)

        flash(
            "Service request submitted successfully! Please wait for your request to be reviewed and confirmed.",
            category="success",
        )
        return redirect(url_for("home"))
    return render_template("home.html", now=datetime.now())


def send_email(recipient, subject, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)


@app.route("/bookings")
@login_required
def bookings():
    if current_user.email.lower() == os.environ.get("ADMIN_MAIL").lower():
        return redirect(url_for("admin"))
    user_bookings = Service.query.filter_by(user_id=current_user.id).all()
    return render_template("bookings.html", bookings=user_bookings, now=datetime.now())


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.email.lower() == os.environ.get("ADMIN_MAIL").lower():
        service = None
        if request.method == "POST":
            action = request.form.get("action")
            service_id = request.form.get("service_id")
            if action == "search":
                service = Service.query.filter_by(id=int(service_id)).first()
                if not service:
                    flash(f"Service ID {service_id} not found.", category="error")
            elif action == "update":
                confirmed_value = request.form.get("confirmed") == "yes"
                service = Service.query.filter_by(id=int(service_id)).first()
                if service:
                    service.confirmed = confirmed_value
                    db.session.commit()
                    flash(f"Booking #{service_id} updated.", category="success")
                else:
                    flash(f"Service ID {service_id} not found.", category="error")

        sort_by = request.args.get("sort", "id")
        order = request.args.get("order", "asc")
        if sort_by == "id":
            if order == "asc":
                bookings = Service.query.order_by(asc(Service.id)).all()
            else:
                bookings = Service.query.order_by(desc(Service.id)).all()
        elif sort_by == "selected_date":
            if order == "asc":
                bookings = Service.query.order_by(asc(Service.selected_date)).all()
            else:
                bookings = Service.query.order_by(desc(Service.selected_date)).all()
        else:
            bookings = Service.query.order_by(
                desc(Service.selected_date), desc(Service.selected_time)
            ).all()

        sort_orders = {
            "id": "asc" if sort_by != "id" or order == "desc" else "desc",
            "selected_date": (
                "asc" if sort_by != "selected_date" or order == "desc" else "desc"
            ),
        }

        return render_template(
            "admin.html",
            sort_orders=sort_orders,
            bookings=bookings,
            service=service,
            now=datetime.now(),
        )
    else:
        return redirect(url_for("home"))


@app.after_request
def apply_caching(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
