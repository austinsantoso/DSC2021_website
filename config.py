import os
from re import DEBUG
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_UPLOADS_DIR = os.path.join(basedir, "data/images/original")
    PROCESSED_IMAGE_DIR = os.path.join(basedir, "data/images/processed")
    YOLOV5_DIR = os.path.join(basedir, "libraries/yolov5")
    WEIGHTS_PATH = os.path.join(
        basedir, "libraries/yolov5/weights/latest/best.pt")
    PATH_TO_LABELED = os.path.join(YOLOV5_DIR, "runs/detect")
