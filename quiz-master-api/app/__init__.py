from flask import Flask
from app.common.config import Config
from app.extensions import db, migrate, jwt, mail
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.answer import Answer
from app.models.otp import Otp
from app.models.notification import UserPreference, AdminNotificationSetting, ReminderLog, ReportHistory

from app.common.logger import setup_logging
from flask_cors import CORS
from app.api.admin import dashboard_bp, chapter_bp, question_bp, quiz_bp, subject_bp, quiz_status_bp
from app.api.admin.admin_notifications_api import admin_notifications_bp
from app.api.auth import login_bp, register_bp, user_profile_bp
from app.api import swaggerui_blueprint, swagger_spec_bp
from app.api.user.manage_quiz_registration_api import quiz_registration_bp
from app.api.admin.admin_settings_api import admin_settings_bp
from app.api.user.user_settings_api import user_settings_bp
from app.api.admin.report_api import report_bp
from app.api.user.export_api import user_export_bp
from app.api.user.dashboard_api import user_dashboard_bp

def create_admin_user():
    admin = User.create_admin(db.session)
    if admin:
        print("Admin user created successfully!")

def create_student_user():
    student = User.create_student(db.session, email="23f1000704@ds.study.iitm.ac.in", fullname="Jitendra Kumar", password="aaaaaaaa")
    if student:
        print("Student user created successfully!")

def create_default_admin_notification_settings():
    from app.models.notification import AdminNotificationSetting
    from app.extensions import db
    from datetime import time, datetime
    if not AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first():
        daily = AdminNotificationSetting(
            setting_type='daily_reminder',
            reminder_time=time(9, 0),
            reminder_channel='email',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(daily)

    if not AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first():
        monthly = AdminNotificationSetting(
            setting_type='monthly_report',
            report_format='html',
            report_day_of_month=1,
            report_channel='email',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(monthly)
    db.session.commit()

def create_default_user_settings():
    from app.models.user import User
    from app.models.notification import UserPreference
    from app.extensions import db
    from datetime import time, datetime
    users = User.query.all()
    for user in users:
        if not UserPreference.query.filter_by(user_id=user.id).first():
            pref = UserPreference(
                user_id=user.id,
                reminder_time=time(9, 0),
                reminder_channel='email',
                report_format='html',
                receive_weekly=False,
                receive_monthly=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(pref)
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
    )
    setup_logging(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(chapter_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(quiz_status_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(user_profile_bp)
    app.register_blueprint(swaggerui_blueprint, url_prefix='/docs')
    app.register_blueprint(swagger_spec_bp)
    app.register_blueprint(quiz_registration_bp)
    app.register_blueprint(admin_settings_bp)
    app.register_blueprint(admin_notifications_bp, url_prefix='/api')
    app.register_blueprint(user_settings_bp)
    app.register_blueprint(report_bp, url_prefix='/api/admin/report')
    app.register_blueprint(user_export_bp, url_prefix='/api/user/export')
    app.register_blueprint(user_dashboard_bp, url_prefix='/api/user')

    with app.app_context():
        db.create_all()
        create_admin_user()
        create_student_user()
        create_default_admin_notification_settings()
        create_default_user_settings()

    return app
