from app.extensions import db

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', back_populates='chapters')
    description = db.Column(db.String(1024), nullable=True)
    quizzes = db.relationship('Quiz', back_populates='chapter', lazy='dynamic', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Chapter {self.name}>,\
            <description {self.description}>'    
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject_id": self.subject_id,
            "description": self.description,
        }