from datetime import datetime
from app.extensions import db

class Score(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_registration_date = db.Column(db.DateTime, default=datetime.now)
    date_stamp_of_attempt = db.Column(db.DateTime)
    time_stamp_of_attempt = db.Column(db.Time)
    time_stamp_of_submited = db.Column(db.Time)
    total_questions = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=0)
    attempted_questions = db.Column(db.Integer, default=0)
    unattempted_questions = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0) 
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Score {self.id}>,\
            <quiz_id {self.quiz_id}>,\
            <user_id {self.user_id}>,\
            <quiz_registration_date {self.quiz_registration_date}>,\
            <date_stamp_of_attempt {self.date_stamp_of_attempt}>,\
            <time_stamp_of_attempt {self.time_stamp_of_attempt}>,\
            <time_stamp_of_submited {self.time_stamp_of_submited}>,\
            <total_questions {self.total_questions}>,\
            <total_marks {self.total_marks}>,\
            <attempted_questions {self.attempted_questions}>,\
            <unattempted_questions {self.unattempted_questions}>,\
            <total_score {self.total_score}>'