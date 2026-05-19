from app.extensions import db
from datetime import datetime, time

class UserPreference(db.Model):
    __tablename__ = 'user_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    reminder_time = db.Column(db.Time, nullable=True)
    reminder_channel = db.Column(db.String(32), nullable=True)  
    report_format = db.Column(db.String(16), nullable=True, default='html')  
    receive_weekly = db.Column(db.Boolean, default=False)
    receive_monthly = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminNotificationSetting(db.Model):
    __tablename__ = 'admin_notification_setting'
    id = db.Column(db.Integer, primary_key=True)
    setting_type = db.Column(db.String(32), nullable=False)  
    reminder_time = db.Column(db.Time, nullable=True)  
    reminder_channel = db.Column(db.String(32), nullable=True, default='email') 
    report_format = db.Column(db.String(16), nullable=True, default='html')  
    report_day_of_month = db.Column(db.Integer, nullable=True, default=1)  
    report_channel = db.Column(db.String(32), nullable=True, default='email') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReminderLog(db.Model):
    __tablename__ = 'reminder_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    channel = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False, default='sent')

class ReportHistory(db.Model):
    __tablename__ = 'report_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(7), nullable=True)  
    report_type = db.Column(db.String(20), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')  
    filename = db.Column(db.String(256), nullable=True) 
    file_path = db.Column(db.String(512), nullable=True) 
    task_id = db.Column(db.String(256), nullable=True) 
    error_message = db.Column(db.Text, nullable=True) 
    
    user = db.relationship('User', backref=db.backref('report_history', lazy=True))
    
    def __repr__(self):
        return f'<ReportHistory {self.user_id} - {self.month} - {self.report_type}>'

class ExportJob(db.Model):
    __tablename__ = 'export_job'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_type = db.Column(db.String(32), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    file_path = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(32), nullable=False, default='pending')
    message = db.Column(db.Text, nullable=True)
