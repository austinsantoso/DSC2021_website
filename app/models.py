from flask_table.columns import ButtonCol, LinkCol
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_table import Table, Col


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class PictureEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_name = db.Column(db.String(128))
    acumen_count_gt = db.Column(db.Integer)
    handwritten_count_gt = db.Column(db.Integer)
    anomalies_bbox_gt = db.Column(db.String(128))
    # download = db.Column(db.String(128))

    def __repr__(self):
        return '<Image {}, by User {}, with ID {}>'.format(self.image_name, self.user_id, self.id)


class PictureEntryTable(Table):
    image_name = Col('Name')
    acumen_count_gt = Col('acumen_count_gt')
    handwritten_count_gt = Col('handwritten_count_gt')
    anomalies_bbox_gt = Col('anomalies_bbox_gt')
    download = LinkCol('download', url_kwargs=dict(
        id='id'), endpoint='downloadProcessed')
