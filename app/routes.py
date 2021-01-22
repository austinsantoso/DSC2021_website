from re import T
from flask import render_template, flash, redirect, url_for, request
from flask.helpers import send_file
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import PictureEntry, PictureEntryTable, User
from werkzeug.urls import url_parse
import os
from subprocess import Popen
import sys


from flask_table import Table, Col


@app.route('/')
@app.route('/index')
@login_required
def index():
    table = PictureEntryTable(PictureEntry.query.all())
    return render_template('index.html', table=table)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/table')
def table():
    table = PictureEntryTable(PictureEntry.query.all())
    return render_template('table.html', table=table)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    allowed_extension = ["JPEG", "JPG", "PNG"]
    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in allowed_extension:
        return True
    else:
        return False


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:

            image = request.files["image"]
            # update the database with the corresponding file name
            newEntry = PictureEntry(
                user_id=current_user.id,
                image_name=image.filename)

            file_type = image.filename.split(".", 1)[1]
            print(newEntry)
            print(image)
            db.session.add(newEntry)
            db.session.commit()
            print(newEntry)
            # newEntry.download = "/download-processed/" + str(newEntry.id)

            new_file_dir = os.path.join(
                app.config["IMAGE_UPLOADS_DIR"], str(newEntry.id) + "." + file_type)
            image.save(new_file_dir)

            # process the image, send to out pipeline
            # !python detect.py --img 640 --source '/content/drive/MyDrive/NUSTATS TINTENTHEUS/FORMATTED/' --weights '//content/drive/MyDrive/NUSTATS TINTENTHEUS/Directories (+ chip haram)/yolov5/runs/train/exp9/weights/best.pt' --iou-thres 0.25 --conf-thres 0.4 --save-txt
            os.system("cd libraries/yolov5 && ls && ../../venv/bin/python3 detect.py --img 640 --weights '{}' --iou-thres 0.25 --conf-thres 0.4 --save-txt --name {} --source {}".format(
                app.config["WEIGHTS_PATH"],
                str(newEntry.id),
                new_file_dir
            ))

            # update out db

            # get the number of acumen count from txt file
            base_output_dir = os.path.join(
                app.config["YOLOV5_DIR"], "runs/detect")
            cur_output_dir = os.path.join(base_output_dir, str(newEntry.id))

            f = open(os.path.join(cur_output_dir,
                                  "labels/" + str(newEntry.id) + ".txt"))

            lines = f.readlines()
            newEntry.acumen_count_gt = len(lines)
            db.session.flush()
            db.session.commit()

            return redirect(url_for('index'))

    return render_template("upload_image.html")


@app.route('/download-processed/<id>', methods=["GET"])
def downloadProcessed(id=None):
    print("Printing id", id)
    path = os.path.join(app.config["PATH_TO_LABELED"], id + "/" + id + ".jpg")
    print(path)
    return send_file(path, as_attachment=True)
