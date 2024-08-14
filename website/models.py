from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Marke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150),unique=True,nullable=False)

class Vape(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    geschmack = db.Column(db.String(150))
    zuege = db.Column(db.Integer)
    marke = db.Column(db.String(150))
    image = db.Column(db.String(150))
    anzahl = db.Column(db.Integer)

class Reserved_vape(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    anzahl = db.Column(db.Integer)
    person = db.Column(db.String(150))
    owner = db.Column(db.String(150))
    geschmack = db.Column(db.String(150))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    notes = db.relationship('Note')
