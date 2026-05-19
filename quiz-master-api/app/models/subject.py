from app.extensions import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    chapters = db.relationship('Chapter', back_populates='subject', lazy='dynamic', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Subject {self.name}>,\
            <description {self.description}>'


    