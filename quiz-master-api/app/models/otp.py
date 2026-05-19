from datetime import datetime
from app.extensions import db

class Otp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, nullable=False)
    opt_code = db.Column(db.String(512), nullable=False)
    active = db.Column(db.Integer, nullable=False, default=1)
    send_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    send_time= db.Column(db.Time, nullable=False, default=datetime.now().time())
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Otp {self.id}>,\
            <user_id {self.user_id}>,\
            <opt_code {self.opt_code}>,\
            <active {self.active}>,\
            <send_date {self.send_date}>,\
            <send_time {self.send_time}>'