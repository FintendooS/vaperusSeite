import sqlalchemy
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.exceptions import BadRequestKeyError

from .models import Vape, Marke
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename
import os
from . import db, UPLOAD_FOLDER

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
    vapes = Vape.query.all()
    for vape in vapes:
        vape.marke = str(vape.marke).capitalize()
    return render_template('home.html', user=current_user, marken=getMarkenList(), vapes=vapes,
                           upload_folder=UPLOAD_FOLDER)


def getMarkenList():
    markenList = []
    marken = Marke.query.all()
    for marke in marken:
        markenList.append(str(marke.name).capitalize())
    return markenList
