from app.common.enums  import QUIZ_STATUSES
from app.extensions import db
from datetime import datetime

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', back_populates='quizzes')
    description = db.Column(db.String(1024), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(128), nullable=False, default=QUIZ_STATUSES[0])
    questions = db.relationship('Question', back_populates='quiz', lazy='dynamic', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    @property
    def title(self):
        """Alias for name to maintain compatibility"""
        return self.name
    
    def __repr__(self):
        return f'<Quiz {self.name}>,\
            <chapter_id {self.chapter_id}>,\
            <remarks {self.remarks}>,\
            <started_date {self.started_date}>,\
            <end_date {self.end_date}>,\
            <duration {self.duration}>,\
            <status {self.status}>'

