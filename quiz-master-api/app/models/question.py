from app.extensions import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(4096), nullable=False)
    option1 = db.Column(db.String(4096), nullable=False)
    option2 = db.Column(db.String(4096), nullable=False)
    option3 = db.Column(db.String(4096), nullable=False)
    option4 = db.Column(db.String(4096), nullable=False)
    answer = db.Column(db.String(4096), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=0)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    quiz = db.relationship('Quiz', back_populates='questions')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<Question {self.question}>,\
            <option1 {self.option1}>,\
            <option2 {self.option2}>,\
            <option3 {self.option3}>,\
            <option4 {self.option4}>,\
            <answer {self.answer}>,\
            <marks {self.marks}>,\
            <quiz_id {self.quiz_id}>'
