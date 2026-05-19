from app.extensions import db
from werkzeug.security import generate_password_hash
from app.common.enums  import USER_ROLE, USER_STATUS
from app.models.user_profile import UserProfile
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=USER_ROLE[0])
    status = db.Column(db.String(50), nullable=False, default=USER_STATUS[0])
    last_login = db.Column(db.DateTime, nullable=True)
    user_profile = db.relationship('UserProfile', back_populates='user', uselist=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<User {self.fullname}>,\
            <email {self.email}>,\
            <fullname {self.fullname}>,\
            <role {self.role}>,\
            <status {self.status}>'
    
    def __init__(self, email, fullname, password, role=USER_ROLE[0], status=USER_STATUS[0]):
        self.email = email
        self.fullname = fullname
        self.password = generate_password_hash(password)
        self.role = role
        self.status = status
    
    def has_role(self, role):
        return role == self.role
    
    @property
    def username(self):
        """Alias for fullname to maintain compatibility"""
        return self.fullname

    @classmethod
    def create_admin(cls, db_session):
        admin = cls.query.filter_by(email="admin@assessmentplatform.com").first()
        if not admin:
            admin = cls(
                fullname="Distributed Assessment Platform",
                email="admin@assessmentplatform.com",
                password="aaaaaaaa", 
                role=USER_ROLE[1] 
            )
            db_session.add(admin)
            db_session.commit()
            admin_profile = UserProfile(user_id=admin.id, profile_picture="admin.jpg")
            db_session.add(admin_profile)
            db_session.commit()
            return admin
        return None

    @classmethod
    def create_student(cls, db_session, email, fullname, password):
        student = cls.query.filter_by(email=email).first()
        if not student:
            student = cls(
                fullname=fullname,
                email=email,
                password=password 
            )
            db_session.add(student)
            db_session.commit()
            student_profile = UserProfile(user_id=student.id)
            db_session.add(student_profile)
            db_session.commit()
            return student
        return None