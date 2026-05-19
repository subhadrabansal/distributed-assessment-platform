from app.models.notification import AdminNotificationSetting, UserPreference, ReminderLog
from app.models.user import User
from app.models.quiz import Quiz
from app.models.score import Score
from app.extensions import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReminderService:
    
    @staticmethod
    def send_daily_reminders():
        """
        Send daily reminders to users via G-Chat (email) based on:
        1. Users who haven't visited recently
        2. New quizzes created that are relevant to them
        """
        logger.info("Daily reminders task started")
        
        daily_setting = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
        if not daily_setting or not daily_setting.reminder_time:
            logger.info("Daily reminders not configured")
            return "Daily reminders not configured"
        
        return ReminderService.send_daily_reminders_at_time(
            daily_setting.reminder_time.hour, 
            daily_setting.reminder_time.minute
        )
    
    @staticmethod
    def send_daily_reminders_at_time(hour, minute):
        """
        Send daily reminders to users who have set this specific time preference
        """
        from datetime import time
        target_time = time(hour, minute)
        
        logger.info(f"Daily reminders task started for time {hour:02d}:{minute:02d}")
        
        daily_setting = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
        if not daily_setting or not daily_setting.reminder_time:
            logger.info("Daily reminders not configured globally")
            return "Daily reminders not configured globally"
        
        users = ReminderService._get_users_for_time(target_time, daily_setting.reminder_time)
        reminder_count = 0
        
        for user in users:
            try:
                if user.role == 'admin':
                    continue
                
                should_send_reminder, reminder_reasons, unregistered_quizzes = ReminderService._check_reminder_conditions(user)
                
                if should_send_reminder and reminder_reasons:
                    if ReminderService._send_reminder_to_user(user, reminder_reasons, unregistered_quizzes, daily_setting):
                        reminder_count += 1
                        
            except Exception as e:
                logger.error(f"Error processing reminders for user {user.id}: {str(e)}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"Daily reminders task completed for {hour:02d}:{minute:02d}. Sent {reminder_count} reminders.")
        except Exception as e:
            logger.error(f"Error committing reminder logs: {str(e)}")
            db.session.rollback()
        
        return f"Sent {reminder_count} daily reminders at {hour:02d}:{minute:02d}"
    
    @staticmethod
    def _get_users_for_time(target_time, admin_default_time):
        """Get users who should receive reminders at the specified time"""
        users_with_preference = User.query.join(UserPreference).filter(
            User.status == 'active',
            UserPreference.reminder_time == target_time,
            UserPreference.reminder_channel.in_(['email', 'gchat'])
        ).all()
        
        users_without_preference = []
        if target_time == admin_default_time:
            users_without_preference = User.query.outerjoin(UserPreference).filter(
                User.status == 'active',
                db.or_(
                    UserPreference.id.is_(None), 
                    UserPreference.reminder_time.is_(None)  
                )
            ).all()
            
  
            users_without_preference = [
                user for user in users_without_preference 
                if not hasattr(user, 'user_preference') or 
                   not user.user_preference or 
                   not user.user_preference.reminder_channel or 
                   user.user_preference.reminder_channel in ['email', 'gchat']
            ]
        

        all_users = list(set(users_with_preference + users_without_preference))
        
        logger.info(f"Found {len(users_with_preference)} users with time preference {target_time} and {len(users_without_preference)} users using default time")
        
        return all_users
    
    @staticmethod
    def _check_reminder_conditions(user):
        """Check if user needs a reminder and return conditions"""
        should_send_reminder = False
        reminder_reasons = []
        
        if not user.last_login or user.last_login < datetime.now() - timedelta(days=3):
            should_send_reminder = True
            last_visit = user.last_login.strftime('%d-%m-%Y') if user.last_login else 'Never'
            reminder_reasons.append(f"You haven't visited since {last_visit}")
        
        now = datetime.now()
        
        ongoing_quizzes = Quiz.query.filter(
            Quiz.start_date <= now,
            Quiz.end_date >= now
        ).all()
        
        upcoming_quizzes = Quiz.query.filter(
            Quiz.start_date > now,
            Quiz.start_date <= now + timedelta(days=7)
        ).all()
        
        all_relevant_quizzes = ongoing_quizzes + upcoming_quizzes
        
        registered_quiz_ids = set(
            row.quiz_id for row in Score.query.filter_by(user_id=user.id)
            .filter(Score.quiz_registration_date.isnot(None)).all()
        )
        
        unregistered_quizzes = [q for q in all_relevant_quizzes if q.id not in registered_quiz_ids]
        
        if unregistered_quizzes:
            should_send_reminder = True
            ongoing_count = len([q for q in unregistered_quizzes if q in ongoing_quizzes])
            upcoming_count = len([q for q in unregistered_quizzes if q in upcoming_quizzes])
            
            if ongoing_count > 0:
                reminder_reasons.append(f"{ongoing_count} ongoing quiz(es) available")
            if upcoming_count > 0:
                reminder_reasons.append(f"{upcoming_count} upcoming quiz(es) starting soon")
        
        recent_quizzes = Quiz.query.filter(
            Quiz.created_at >= datetime.now() - timedelta(days=1)
        ).all()
        
        new_unregistered = [q for q in recent_quizzes if q.id not in registered_quiz_ids]
        if new_unregistered:
            should_send_reminder = True
            reminder_reasons.append(f"{len(new_unregistered)} new quiz(es) created")
        
        return should_send_reminder, reminder_reasons, unregistered_quizzes
    
    @staticmethod
    def _send_reminder_to_user(user, reminder_reasons, unregistered_quizzes, daily_setting):
        """Send reminder email to a specific user"""
        today = datetime.now().date()
        existing_reminder = ReminderLog.query.filter_by(
            user_id=user.id
        ).filter(
            db.func.date(ReminderLog.sent_at) == today
        ).first()
        
        if existing_reminder:
            return False
        
        subject = "📚 Distributed Assessment Platform - Daily Reminder"
        
        quiz_details = ReminderService._format_quiz_details(unregistered_quizzes)
        
        message_body = ReminderService._create_text_message(
            user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting
        )
        
        try:
            msg = Message(
                subject=subject,
                sender=("Distributed Assessment Platform", "noreply@assessmentplatform.com"),
                recipients=[user.email],
                body=message_body
            )
            
            html_body = ReminderService._create_html_message(
                user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting
            )
            
            msg.html = html_body
            mail.send(msg)
            
            reminder_log = ReminderLog(
                user_id=user.id,
                sent_at=datetime.now(),
                channel='gchat-email',
                message=message_body,
                status='sent'
            )
            db.session.add(reminder_log)
            
            logger.info(f"Reminder sent to user {user.id} ({user.email})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reminder to user {user.id}: {str(e)}")
            reminder_log = ReminderLog(
                user_id=user.id,
                sent_at=datetime.now(),
                channel='gchat-email',
                message=message_body,
                status='failed'
            )
            db.session.add(reminder_log)
            return False
    
    @staticmethod
    def _send_manual_reminder_to_user(user, reminder_reasons, unregistered_quizzes, daily_setting):
        """Send manual reminder email to a specific user (bypasses duplicate checks)"""
        subject = "📚 Distributed Assessment Platform - Daily Reminder [Manual]"
        
        quiz_details = ReminderService._format_quiz_details(unregistered_quizzes)
        
        message_body = ReminderService._create_text_message(
            user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting
        )
        
        try:
            msg = Message(
                subject=subject,
                sender=("Distributed Assessment Platform", "noreply@assessmentplatform.com"),
                recipients=[user.email],
                body=message_body
            )
            
            html_body = ReminderService._create_html_message(
                user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting
            )
            
            msg.html = html_body
            mail.send(msg)
            
            reminder_log = ReminderLog(
                user_id=user.id,
                sent_at=datetime.now(),
                channel='gchat-email-manual',
                message=message_body,
                status='sent'
            )
            db.session.add(reminder_log)
            
            logger.info(f"Manual reminder sent to user {user.id} ({user.email})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send manual reminder to user {user.id}: {str(e)}")
            reminder_log = ReminderLog(
                user_id=user.id,
                sent_at=datetime.now(),
                channel='gchat-email-manual',
                message=message_body,
                status='failed'
            )
            db.session.add(reminder_log)
            return False
    
    @staticmethod
    def _format_quiz_details(unregistered_quizzes):
        """Format quiz details for display"""
        quiz_details = []
        now = datetime.now()
        
        for quiz in unregistered_quizzes[:5]:  
            status = "🔴 Ongoing" if quiz.start_date <= now <= quiz.end_date else "🟡 Upcoming"
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else 'N/A'
            quiz_details.append(f"• {status} {quiz.name} ({subject_name})")
        
        return quiz_details
    
    @staticmethod
    def _create_text_message(user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting):
        """Create plain text message body"""
        return f"""
Hello {user.fullname or user.email},

{' and '.join(reminder_reasons)}. 

📖 Available Quizzes:
{chr(10).join(quiz_details)}
{chr(10) + "...and more!" if len(unregistered_quizzes) > 5 else ""}

🎯 Visit Distributed Assessment Platform to:
• Register for relevant quizzes
• Attempt ongoing quizzes
• Check your progress

Good luck with your studies! 📚✨

---
Distributed Assessment Platform Notification System
    
    @staticmethod
    def _create_html_message(user, reminder_reasons, quiz_details, unregistered_quizzes, daily_setting):
        """Create HTML message body with G-Chat styling"""
        return f"""
        <div style="font-family: 'Google Sans', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
            <div style="background: white; border-radius: 8px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="border-left: 4px solid #4285f4; padding-left: 16px; margin-bottom: 24px;">
                    <h2 style="color: #202124; margin: 0; font-size: 20px;">📚 Distributed Assessment Platform Daily Reminder</h2>
                </div>
                
                <p style="color: #5f6368; font-size: 16px; line-height: 1.5;">
                    Hello <strong>{user.fullname or user.email}</strong>,
                </p>
                
                <p style="color: #202124; font-size: 16px; line-height: 1.5;">
                    {' and '.join(reminder_reasons)}.
                </p>
                
                <div style="background: #f1f3f4; border-radius: 8px; padding: 16px; margin: 20px 0;">
                    <h3 style="color: #202124; margin: 0 0 12px 0; font-size: 16px;">📖 Available Quizzes:</h3>
                    {'<br>'.join(quiz_details)}
                    {'<br><em style="color: #5f6368;">...and more!</em>' if len(unregistered_quizzes) > 5 else ''}
                </div>
                
                <div style="background: #e8f0fe; border-radius: 8px; padding: 16px; margin: 20px 0;">
                    <h3 style="color: #1a73e8; margin: 0 0 8px 0; font-size: 16px;">🎯 What you can do:</h3>
                    <ul style="color: #202124; margin: 8px 0; padding-left: 20px; line-height: 1.6;">
                        <li>Register for relevant quizzes</li>
                        <li>Attempt ongoing quizzes</li>
                        <li>Check your progress</li>
                    </ul>
                </div>
                
                <p style="color: #5f6368; font-size: 14px; text-align: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid #dadce0;">
                    Good luck with your studies! 📚✨<br>
                    <em>Distributed Assessment Platform Notification System</em>
                </p>
            </div>
        </div>
        """

    @staticmethod
    def send_daily_reminders_manual():
        """
        Manually send daily reminders to ALL active users without any time restrictions
        """
        logger.info("Manual daily reminders task started")
        
        active_users = User.query.filter_by(status='active').all()
        
        sent_count = 0
        
        for user in active_users:
            try:
                if user.role == 'admin':
                    continue
                
                user_pref = UserPreference.query.filter_by(user_id=user.id).first()
                
                should_send_reminder, reminder_reasons, unregistered_quizzes = ReminderService._check_reminder_conditions(user)
                
                daily_setting = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
                if not daily_setting:
                    logger.warning("Daily reminder settings not found")
                    continue
                
                if reminder_reasons and ReminderService._send_manual_reminder_to_user(user, reminder_reasons, unregistered_quizzes, daily_setting):
                    sent_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending manual daily reminder to user {user.id}: {str(e)}")
                continue
        
        result_message = f"Sent {sent_count} manual daily reminders to active users"
        logger.info(result_message)
        return result_message
