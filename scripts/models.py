from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////usr/local/data/tasks.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    batchdir = db.Column(db.String(256))
    datadir = db.Column(db.String(256))
    result = db.Column(db.String(256))

    def __init__(self, id, batchdir, datadir):
        self.id = id  
        self.batchdir = batchdir
        self.datadir = datadir

    def __repr__(self):
        return '<Task Record for %r>' % self.datadir

if __name__ == "__main__":
    print "Creating database at %s" % app.config['SQLALCHEMY_DATABASE_URI']
    db.create_all()

