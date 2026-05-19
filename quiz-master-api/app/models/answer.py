from datetime import datetime
from app.extensions import db

class Answer(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    correct_answer =  db.Column(db.Integer)
    user_answer =  db.Column(db.Integer)
    question_marks = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Answer {self.id}>,\
            <quiz_id {self.quiz_id}>,\
            <user_id {self.user_id}>,\
            <question_id {self.question_id}>,\
            <correct_answer {self.correct_answer}>,\
            <user_answer {self.user_answer}>,\
            <question_marks {self.question_marks}>'