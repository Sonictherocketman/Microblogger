""" Model of a Microblog Message. """

from datetime import datetime

from shared import db

class Message(db.Model):
    """ Models a standard microblog message. """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    username = db.Column(db.Unicode(20))
    user_link = db.Column(db.Unicode(200))
    message = db.Column(db.Unicode(200))
    date = db.Column(db.DateTime())

    # Link back to the user they belong to.
    user_pk = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                    backref=db.backref('messages', lazy='dynamic'))

    def __init__(self, user_id, username, user_link, message, date):
        self.user_id = user_id
        self.username = username
        self.user_link = user_link
        self.message = message
        if date is None:
            date = datetime.utcnow()
        self.date = date
