from app import app, db
from app.models import PictureEntry, User


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Picture_Entry': PictureEntry}
