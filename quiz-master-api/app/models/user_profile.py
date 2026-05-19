from app.extensions import db
from app.common.enums  import DEFAULT_IMAGE

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_picture = db.Column(db.String(1024), nullable=True, default=DEFAULT_IMAGE)
    phone_number = db.Column(db.String(15), nullable=True)   
    date_of_birth = db.Column(db.DateTime, nullable=True)
    qualification = db.Column(db.String(512), nullable=True)
    subject = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    user = db.relationship('User', back_populates='user_profile')

    def __repr__(self):
        return f'<UserProfile {self.id}>,\
            <user_id {self.user_id}>,\
            <profile_picture {self.profile_picture}>,\
            <phone_number {self.phone_number}>,\
            <date_of_birth {self.date_of_birth}>,\
            <qualification {self.qualification}>,\
            <subject {self.subject}>'
    
    def __init__(self, user_id, image_file=DEFAULT_IMAGE, profile_picture=None, phone_number=None, date_of_birth=None, qualification=None, subject=None):
        self.user_id = user_id
        self.image_file = image_file
        self.profile_picture = profile_picture
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.qualification = qualification
        self.subject = subject
