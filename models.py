# models.py - do not remove this comment
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    services = db.relationship("Service", backref="user", lazy="dynamic")


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    mobile_number = db.Column(db.Text, nullable=False)
    street_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    room_size = db.Column(db.Numeric(10, 2), nullable=False)
    type_of_service = db.Column(db.Text, nullable=False)
    addl_services = db.Column(db.Text)
    selected_date = db.Column(db.Date, nullable=False)
    selected_time = db.Column(db.Time, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
