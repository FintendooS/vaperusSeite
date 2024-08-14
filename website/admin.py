import sqlalchemy
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, make_response
from werkzeug.exceptions import BadRequestKeyError

from .models import Vape, Marke, Reserved_vape
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename
import os
from . import db, UPLOAD_FOLDER, views, ALLOWED_EXTENSIONS

admin = Blueprint('admin', __name__)


@admin.route('/marke_add', methods=['GET', 'POST'])
@login_required
def addMarke():
    if request.method == 'POST':
        try:
            for data in request.form:
                if not request.form[data].strip():
                    flash("Du musst einen Namen eingeben", category='error')
                    return redirect(url_for('views.addMarke'))
            try:
                marke = Marke(name=request.form['marke'].lower())
                db.session.add(marke)
                db.session.commit()

                flash(f"Du hast die Marke {str(marke.name).capitalize()} hinzugefügt!", "success")
                print(f"Marke {str(marke.name).capitalize()} wurde hinzugefügt!")
            except sqlalchemy.exc.IntegrityError:
                flash(f"Die Marke {str(marke.name).capitalize()} gibt es schon!", "error")
        except BadRequestKeyError:
            try:
                marke = request.form['deleteMarke']
                Marke.query.filter_by(name=marke.lower()).delete()
                db.session.commit()
                flash(f'Du hast die Marke {str(marke).capitalize()} entfernt!')
            except BadRequestKeyError:
                pass
    else:
        print(request.form)
    return render_template("marke_add.html", user=current_user, marken=views.getMarkenList())


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getExtensions(filename):
    return filename.rsplit('.', 1)[1].lower()



def vapeFileNameGenerator(geschmack, marke, anzahl):
    return (str(anzahl).lower() + "_" + geschmack.lower() + "_" + marke.lower()).replace(" ", "_") + ""




@admin.route('/uploadfile', methods=['GET', 'POST'])
@login_required
def uploadfile():
    if request.method == 'POST':
        for data in request.form:
            if not request.form[data].strip():
                flash("Du musst alle angaben erfüllen", category='error')
                return redirect(url_for('admin.uploadfile'))
        if 'file' not in request.files:
            flash("Kein Bild ausgewählt", category='error')
            return redirect(url_for('admin.uploadfile'))
        else:
            file = request.files['file']
            if file.filename == '':
                flash("Kein Bild ausgewählt", category='error')
                return redirect(url_for('admin.uploadfile'))
            try:
                marke = request.form['marke']
            except BadRequestKeyError:
                flash("Du musst alle angaben erfüllen", category='error')
                return redirect(url_for('admin.uploadfile'))
            if file and allowed_file(file.filename):
                geschmack = request.form['geschmack']
                zuege = request.form['züge']
                anzahl = request.form['anzahl']
                BildName = (vapeFileNameGenerator(geschmack, marke, anzahl) + "." + getExtensions(file.filename))
                newVape = Vape(
                    geschmack=geschmack,
                    zuege=zuege,
                    marke=marke,
                    image=BildName,
                    anzahl=anzahl,
                )

                filename = secure_filename(BildName)
                file.save(os.path.join(UPLOAD_FOLDER, filename))

                db.session.add(newVape)
                db.session.commit()

                flash(f"Du hast die Vape {geschmack} {marke} mit {zuege} Zügen hinzugefügt!", "success")
                print(f"Die Vape {geschmack} {marke} {zuege} Züge {anzahl} {BildName} wurde hinzugefügt!")
    return render_template("uploadfile.html", user=current_user, marken=views.getMarkenList())

@admin.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), 'uploads/' + filename)

@admin.route('/delete_vape')
@login_required
def delete_vape():
    vapes = Vape.query.all()
    reservieren = Reserved_vape.query.all()

    return render_template('remove_vape.html',user=current_user,vapes=vapes, reservierungen = reservieren)


@admin.route('/rm_vape/<id>', methods=['GET','POST'])
def remove_vape(id):
    anzahl = request.form['anzahl_to_remove']
    vape = Vape.query.filter_by(id=id).first()
    vape.anzahl -= int(anzahl)

    if vape.anzahl <= 0:
        db.session.delete(vape)
        db.session.commit()
        flash('Du hast eine Vape vollständing verkauft und somit entfernt!', 'success')
        return redirect(url_for('admin.delete_vape'))

    db.session.commit()
    flash(f'Du hast eine Vape {anzahl}x verkauft!','success')
    return redirect(url_for('admin.delete_vape'))

@admin.route('/reservierung_vape/<id>', methods=['GET','POST'])
def reservieren(id):
    anzahl = request.form['anzahl_to_reserve']
    userfor = request.form['reservere_for']
    vape = Vape.query.filter_by(id=id).first()

    owner = current_user.username


    newReserve = Reserved_vape(
        anzahl=anzahl,
        person=userfor,
        owner=owner,
        geschmack=vape.geschmack,
        )

    db.session.add(newReserve)

    db.session.commit()
    print(f"{anzahl}x {newReserve.geschmack} reserviert für {userfor} von {current_user.username}")
    flash(f'Du hast {anzahl}x {newReserve.geschmack} reserviert für {userfor}!','success')
    return redirect(url_for('admin.delete_vape'))

@admin.route('/rm_reservevape/<id>', methods=['GET','POST'])
def reservierung_remove(id):
    reserve = Reserved_vape.query.filter_by(id=id).first()
    db.session.delete(reserve)

    db.session.commit()
    return redirect(url_for('admin.delete_vape'))

@admin.route('/rm_reservevape_succed/<id>/<vapeid>', methods=['GET','POST'])
def reservierung_succed(id,vapeid):
    reserve = Reserved_vape.query.filter_by(id=id).first()
    db.session.delete(reserve)

    vape = Vape.query.filter_by(id=vapeid).first()
    vape.anzahl -= int(reserve.anzahl)

    if vape.anzahl <= 0:
        db.session.delete(vape)
        db.session.commit()
        flash('Du hast eine Vape vollständing verkauft und somit entfernt!', 'success')
        return redirect(url_for('admin.delete_vape'))

    db.session.commit()
    return redirect(url_for('admin.delete_vape'))