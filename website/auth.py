import sqlalchemy
from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import PendingRollbackError

from .models import User, Marke
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, views
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username.startswith('admin_createACC/'):
            new = username.split("/")[1]

            try:
                new_user = User(username=new,
                                password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()

                flash(f'Account erstellt: {new} Passwort: {password}', 'success')
                print(f'Account erstellt: {new} Passwort: {password}', 'success')
                return redirect(url_for('views.home'))
            except sqlalchemy.exc.IntegrityError or PendingRollbackError:
                flash(
                    f'Account konnte nicht erstellt werden, da ein Account mit diesem Benutzernamen bereits existiert!',
                    'error')
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    flash(f'Erfolgreich als {username} eingeloggt!', 'success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash(f'Du hast ein falsches Passwort eingegeben!', 'error')
            else:
                flash(f'Der Benutzer {username} existiert nicht!', 'error')

    return render_template('login.html', user=current_user, marken=views.getMarkenList())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'Du hast dich ausgeloggt!', 'success')
    return redirect(url_for('views.home'))


def vapeFileNameGenerator(geschmack, marke, anzahl):
    return (str(anzahl).lower() + "_" + geschmack.lower() + "_" + marke.lower()).replace(" ", "_") + ""
