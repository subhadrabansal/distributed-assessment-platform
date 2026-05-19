from app.models.notification import AdminNotificationSetting, UserPreference, ReportHistory
from app.models.user import User
from app.models.quiz import Quiz
from app.models.score import Score
from app.models.answer import Answer
from app.extensions import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
from calendar import monthrange
import logging

logger = logging.getLogger(__name__)

class ReportService:
    
    @staticmethod
    def send_monthly_reports():
        """
        Generate and send monthly activity reports to all users
        """
        logger.info("Monthly reports task started")
        
        monthly_setting = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        if not monthly_setting or not monthly_setting.reminder_time:
            logger.info("Monthly reports not configured")
            return "Monthly reports not configured"
        
        now = datetime.now()
        if now.month == 1:
            report_month = 12
            report_year = now.year - 1
        else:
            report_month = now.month - 1
            report_year = now.year
            
        month_str = f"{report_year}-{report_month:02d}"
        
        logger.info(f"Generating monthly reports for {month_str}")
        
        users = User.query.filter_by(status='active').all()
        report_count = 0
        
        for user in users:
            try:
                if user.role == 'admin':
                    continue
                
                user_pref = UserPreference.query.filter_by(user_id=user.id).first()
                
                if user_pref and not user_pref.receive_monthly:
                    continue
                
                existing_report = ReportHistory.query.filter_by(
                    user_id=user.id,
                    month=month_str,
                    report_type='monthly'
                ).first()
                
                if existing_report:
                    logger.info(f"Monthly report already sent to user {user.id} for {month_str}")
                    continue
                
                if ReportService._generate_and_send_monthly_report(user, report_year, report_month, monthly_setting):
                    report_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing monthly report for user {user.id}: {str(e)}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"Monthly reports task completed. Sent {report_count} reports for {month_str}.")
        except Exception as e:
            logger.error(f"Error committing report history: {str(e)}")
            db.session.rollback()
        
        return f"Sent {report_count} monthly reports for {month_str}"
    
    @staticmethod
    def _generate_and_send_monthly_report(user, year, month, monthly_setting):
        """Generate and send monthly report for a specific user"""
        try:
            report_data = ReportService._generate_monthly_report_data(user, year, month)
            
            if not report_data['has_activity']:
                logger.info(f"No activity found for user {user.id} in {year}-{month:02d}")
                return False
            
            subject = f"📊 Distributed Assessment Platform - Monthly Activity Report ({year}-{month:02d})"
            
            html_body = ReportService._create_monthly_report_html(user, report_data, year, month)
            
            text_body = ReportService._create_monthly_report_text(user, report_data, year, month)
            
            msg = Message(
                subject=subject,
                sender=("Distributed Assessment Platform", "noreply@assessmentplatform.com"),
                recipients=[user.email],
                body=text_body,
                html=html_body
            )
            
            mail.send(msg)
            
            report_history = ReportHistory(
                user_id=user.id,
                month=f"{year}-{month:02d}",
                created_at=datetime.now(),
                report_type='monthly',
                status='sent'
            )
            db.session.add(report_history)
            
            logger.info(f"Monthly report sent to user {user.id} ({user.email}) for {year}-{month:02d}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send monthly report to user {user.id}: {str(e)}")
            report_history = ReportHistory(
                user_id=user.id,
                month=f"{year}-{month:02d}",
                created_at=datetime.now(),
                report_type='monthly',
                status='failed'
            )
            db.session.add(report_history)
            return False
    
    @staticmethod
    def _generate_monthly_report_data(user, year, month):
        """Generate comprehensive monthly report data for a user"""
        start_date = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)
        
        monthly_scores = Score.query.filter(
            Score.user_id == user.id,
            Score.date_stamp_of_attempt >= start_date.date(),
            Score.date_stamp_of_attempt <= end_date.date()
        ).all()
        
        if not monthly_scores:
            return {'has_activity': False}
        
        total_quizzes = len(monthly_scores)
        total_score = sum(score.total_score or 0 for score in monthly_scores)
        total_possible = sum(score.total_marks or 0 for score in monthly_scores)
        average_score = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        quiz_details = []
        subject_stats = {}
        
        for score in monthly_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if not quiz:
                continue
                
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else 'Unknown'
            chapter_name = quiz.chapter.name if quiz.chapter else 'Unknown'
            
            quiz_info = {
                'quiz_name': quiz.name,
                'subject': subject_name,
                'chapter': chapter_name,
                'date': score.date_stamp_of_attempt.strftime('%d %b %Y'),
                'score': score.total_score or 0,
                'total_marks': score.total_marks or 0,
                'percentage': (score.total_score / score.total_marks * 100) if score.total_marks > 0 else 0,
                'questions_attempted': score.attempted_questions or 0,
                'total_questions': score.total_questions or 0
            }
            quiz_details.append(quiz_info)
            
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'quizzes': 0,
                    'total_score': 0,
                    'total_possible': 0,
                    'average': 0
                }
            
            subject_stats[subject_name]['quizzes'] += 1
            subject_stats[subject_name]['total_score'] += score.total_score or 0
            subject_stats[subject_name]['total_possible'] += score.total_marks or 0
        
        for subject in subject_stats:
            if subject_stats[subject]['total_possible'] > 0:
                subject_stats[subject]['average'] = (
                    subject_stats[subject]['total_score'] / 
                    subject_stats[subject]['total_possible'] * 100
                )
        
        all_monthly_scores = db.session.query(
            Score.user_id,
            db.func.sum(Score.total_score).label('total_score'),
            db.func.sum(Score.total_marks).label('total_marks')
        ).filter(
            Score.date_stamp_of_attempt >= start_date.date(),
            Score.date_stamp_of_attempt <= end_date.date()
        ).group_by(Score.user_id).subquery()
        
        user_rankings = db.session.query(
            all_monthly_scores.c.user_id,
            (all_monthly_scores.c.total_score / all_monthly_scores.c.total_marks * 100).label('percentage')
        ).filter(
            all_monthly_scores.c.total_marks > 0
        ).order_by(
            db.desc(all_monthly_scores.c.total_score / all_monthly_scores.c.total_marks)
        ).all()
        
        user_rank = None
        total_participants = len(user_rankings)
        for idx, ranking in enumerate(user_rankings):
            if ranking.user_id == user.id:
                user_rank = idx + 1
                break
        
        quiz_details.sort(key=lambda x: x['percentage'], reverse=True)
        best_quiz = quiz_details[0] if quiz_details else None
        worst_quiz = quiz_details[-1] if quiz_details else None
        
        return {
            'has_activity': True,
            'total_quizzes': total_quizzes,
            'total_score': total_score,
            'total_possible': total_possible,
            'average_score': round(average_score, 2),
            'quiz_details': quiz_details,
            'subject_stats': subject_stats,
            'user_rank': user_rank,
            'total_participants': total_participants,
            'best_quiz': best_quiz,
            'worst_quiz': worst_quiz,
            'month_name': datetime(year, month, 1).strftime('%B %Y')
        }
    
    @staticmethod
    def _create_monthly_report_html(user, report_data, year, month):
        """Create HTML version of monthly report"""
        subject_rows = ""
        for subject, stats in report_data['subject_stats'].items():
            subject_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{subject}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: center;">{stats['quizzes']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: center;">{stats['total_score']}/{stats['total_possible']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: center;">{stats['average']:.1f}%</td>
            </tr>
            """
        
        quiz_rows = ""
        for quiz in report_data['quiz_details'][:10]: 
            quiz_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{quiz['quiz_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{quiz['subject']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{quiz['date']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: center;">{quiz['score']}/{quiz['total_marks']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: center;">{quiz['percentage']:.1f}%</td>
            </tr>
            """
        
        ranking_text = f"You ranked #{report_data['user_rank']} out of {report_data['total_participants']} participants" if report_data['user_rank'] else "Ranking not available"
        
        return f"""
        <div style="font-family: 'Google Sans', Arial, sans-serif; max-width: 800px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
            <div style="background: white; border-radius: 8px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 32px; border-bottom: 3px solid #4285f4; padding-bottom: 24px;">
                    <h1 style="color: #1a73e8; margin: 0; font-size: 28px;">📊 Monthly Activity Report</h1>
                    <h2 style="color: #5f6368; margin: 8px 0 0 0; font-size: 20px; font-weight: normal;">{report_data['month_name']}</h2>
                    <p style="color: #5f6368; margin: 8px 0 0 0; font-size: 16px;">Hello <strong style="color: #202124;">{user.fullname}</strong>!</p>
                </div>
                
                <!-- Summary Stats -->
                <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 32px; justify-content: space-around;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; min-width: 150px;">
                        <div style="font-size: 32px; font-weight: bold; margin-bottom: 8px;">{report_data['total_quizzes']}</div>
                        <div style="font-size: 14px; opacity: 0.9;">Quizzes Taken</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; min-width: 150px;">
                        <div style="font-size: 32px; font-weight: bold; margin-bottom: 8px;">{report_data['average_score']:.1f}%</div>
                        <div style="font-size: 14px; opacity: 0.9;">Average Score</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; min-width: 150px;">
                        <div style="font-size: 24px; font-weight: bold; margin-bottom: 8px;">#{report_data['user_rank'] or 'N/A'}</div>
                        <div style="font-size: 14px; opacity: 0.9;">Your Rank</div>
                    </div>
                </div>
                
                <!-- Performance Highlights -->
                <div style="margin-bottom: 32px;">
                    <h3 style="color: #1a73e8; font-size: 20px; margin-bottom: 16px; border-left: 4px solid #1a73e8; padding-left: 12px;">🎯 Performance Highlights</h3>
                    <div style="background: #e8f5e8; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <strong style="color: #2e7d32;">🏆 Best Performance:</strong> 
                        {report_data['best_quiz']['quiz_name']} - {report_data['best_quiz']['percentage']:.1f}% ({report_data['best_quiz']['score']}/{report_data['best_quiz']['total_marks']})
                    </div>
                    <div style="background: #fff3e0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <strong style="color: #ef6c00;">📈 Improvement Area:</strong> 
                        {report_data['worst_quiz']['quiz_name']} - {report_data['worst_quiz']['percentage']:.1f}% ({report_data['worst_quiz']['score']}/{report_data['worst_quiz']['total_marks']})
                    </div>
                    <div style="background: #e3f2fd; border-radius: 8px; padding: 16px;">
                        <strong style="color: #1976d2;">🏅 Monthly Ranking:</strong> 
                        {ranking_text}
                    </div>
                </div>
                
                <!-- Subject-wise Performance -->
                <div style="margin-bottom: 32px;">
                    <h3 style="color: #1a73e8; font-size: 20px; margin-bottom: 16px; border-left: 4px solid #1a73e8; padding-left: 12px;">📚 Subject-wise Performance</h3>
                    <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="padding: 12px; text-align: left; color: #202124; font-weight: 600;">Subject</th>
                                <th style="padding: 12px; text-align: center; color: #202124; font-weight: 600;">Quizzes</th>
                                <th style="padding: 12px; text-align: center; color: #202124; font-weight: 600;">Score</th>
                                <th style="padding: 12px; text-align: center; color: #202124; font-weight: 600;">Average</th>
                            </tr>
                        </thead>
                        <tbody>
                            {subject_rows}
                        </tbody>
                    </table>
                </div>
                
                <!-- Quiz Details -->
                <div style="margin-bottom: 32px;">
                    <h3 style="color: #1a73e8; font-size: 20px; margin-bottom: 16px; border-left: 4px solid #1a73e8; padding-left: 12px;">📝 Quiz Details</h3>
                    <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="padding: 12px; text-align: left; color: #202124; font-weight: 600;">Quiz Name</th>
                                <th style="padding: 12px; text-align: left; color: #202124; font-weight: 600;">Subject</th>
                                <th style="padding: 12px; text-align: left; color: #202124; font-weight: 600;">Date</th>
                                <th style="padding: 12px; text-align: center; color: #202124; font-weight: 600;">Score</th>
                                <th style="padding: 12px; text-align: center; color: #202124; font-weight: 600;">%</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quiz_rows}
                        </tbody>
                    </table>
                    {f'<p style="color: #5f6368; font-style: italic; margin-top: 8px; text-align: center;">Showing top 10 quizzes. Total: {len(report_data["quiz_details"])} quizzes</p>' if len(report_data['quiz_details']) > 10 else ''}
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid #dadce0;">
                    <p style="color: #5f6368; font-size: 14px; margin: 0;">
                        Keep up the great work! 🌟<br>
                        <em>Distributed Assessment Platform Team</em>
                    </p>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def _create_monthly_report_text(user, report_data, year, month):
        """Create text version of monthly report"""
        subject_text = ""
        for subject, stats in report_data['subject_stats'].items():
            subject_text += f"• {subject}: {stats['quizzes']} quizzes, {stats['average']:.1f}% average\n"
        
        quiz_text = ""
        for quiz in report_data['quiz_details'][:5]: 
            quiz_text += f"• {quiz['quiz_name']} ({quiz['subject']}) - {quiz['percentage']:.1f}% on {quiz['date']}\n"
        
        ranking_text = f"You ranked #{report_data['user_rank']} out of {report_data['total_participants']} participants" if report_data['user_rank'] else "Ranking not available"
        
        return f"""
📊 DISTRIBUTED ASSESSMENT PLATFORM - MONTHLY ACTIVITY REPORT
{report_data['month_name']}

Hello {user.fullname}!

📈 MONTHLY SUMMARY
• Total Quizzes Taken: {report_data['total_quizzes']}
• Average Score: {report_data['average_score']:.1f}%
• Total Points: {report_data['total_score']}/{report_data['total_possible']}
• Monthly Ranking: {ranking_text}

🎯 PERFORMANCE HIGHLIGHTS
🏆 Best Performance: {report_data['best_quiz']['quiz_name']} - {report_data['best_quiz']['percentage']:.1f}%
📈 Improvement Area: {report_data['worst_quiz']['quiz_name']} - {report_data['worst_quiz']['percentage']:.1f}%

📚 SUBJECT-WISE PERFORMANCE
{subject_text}

📝 RECENT QUIZZES
{quiz_text}
{'...and more!' if len(report_data['quiz_details']) > 5 else ''}

Keep up the great work! 🌟

---
Distributed Assessment Platform Team
"""
    
    @staticmethod
    def export_user_csv_enhanced(user_id, export_record_id=None):
        """Export individual user's quiz data as CSV with enhanced details and job tracking"""
        import csv
        import os
        from io import StringIO
        
        try:
            if export_record_id:
                from app.models.notification import ReportHistory
                export_record = ReportHistory.query.get(export_record_id)
                if export_record:
                    export_record.status = 'processing'
                    db.session.commit()
            
            user = User.query.get(user_id)
            if not user:
                if export_record:
                    export_record.status = 'failed'
                    db.session.commit()
                return "User not found"
            
            scores = db.session.query(Score, Quiz)\
                .join(Quiz, Score.quiz_id == Quiz.id)\
                .filter(Score.user_id == user_id)\
                .order_by(Score.date_stamp_of_attempt.desc() if Score.date_stamp_of_attempt else Score.id.desc()).all()
            
            if not scores:
                if export_record:
                    export_record.status = 'completed'
                    db.session.commit()
                return "No quiz data found for user"
            
            output = StringIO()
            writer = csv.writer(output)
            
            writer.writerow([
                'Quiz ID', 'Quiz Name', 'Chapter ID', 'Chapter Name', 'Subject ID', 'Subject Name',
                'Date of Quiz', 'Date of Attempt', 'Score Obtained', 'Total Marks', 'Percentage',
                'Questions Attempted', 'Total Questions', 'Completion Status', 'Time Spent (mins)',
                'Registration Date', 'Submission Date', 'Remarks', 
                # 'Rank', 
                'Pass/Fail Status'
            ])
            
            for score, quiz in scores:
                chapter = quiz.chapter
                subject = chapter.subject if chapter else None
                
                percentage = (score.total_score / score.total_marks * 100) if score.total_marks and score.total_marks > 0 else 0
                
                pass_fail = "Pass" if percentage >= 50 else "Fail" if score.total_marks else "N/A"
                
                time_spent = ""
                if score.time_stamp_of_submited and score.date_stamp_of_attempt:
                    try:
                        time_spent = "N/A" 
                    except:
                        time_spent = "N/A"
                
                remarks = ""
                if percentage >= 90:
                    remarks = "Excellent Performance"
                elif percentage >= 75:
                    remarks = "Good Performance"
                elif percentage >= 50:
                    remarks = "Average Performance"
                elif score.total_marks:
                    remarks = "Needs Improvement"
                else:
                    remarks = "Not Completed"
                
                writer.writerow([
                    quiz.id,
                    quiz.name or "N/A",
                    chapter.id if chapter else "N/A",
                    chapter.name if chapter else "N/A",
                    subject.id if subject else "N/A",
                    subject.name if subject else "N/A",
                    quiz.start_date.strftime('%Y-%m-%d') if quiz.start_date else "N/A",
                    score.date_stamp_of_attempt.strftime('%Y-%m-%d') if score.date_stamp_of_attempt else "N/A",
                    score.total_score or 0,
                    score.total_marks or 0,
                    f"{percentage:.1f}%",
                    score.attempted_questions or 0,
                    score.total_questions or 0,
                    'Submitted' if score.time_stamp_of_submited else 'In Progress',
                    time_spent,
                    score.quiz_registration_date.strftime('%Y-%m-%d') if score.quiz_registration_date else "N/A",
                    score.time_stamp_of_submited.strftime('%Y-%m-%d %H:%M') if score.time_stamp_of_submited else "N/A",
                    remarks,
                    # "N/A",  
                    pass_fail
                ])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_{user_id}_quiz_report_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            
            os.makedirs('exports', exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                csvfile.write(output.getvalue())
            
            if export_record:
                export_record.status = 'completed'
                db.session.commit()
            
            logger.info(f"Enhanced CSV export completed for user {user_id}: {filepath}")
            return f"CSV exported successfully: {filepath}"
            
        except Exception as e:
            logger.error(f"Error exporting enhanced CSV for user {user_id}: {str(e)}")
            
            if export_record_id:
                try:
                    from app.models.notification import ReportHistory
                    export_record = ReportHistory.query.get(export_record_id)
                    if export_record:
                        export_record.status = 'failed'
                        db.session.commit()
                except:
                    pass
            
            return f"Export failed: {str(e)}"
    
    @staticmethod
    def export_user_csv(user_id):
        """Legacy method - calls the enhanced version without job tracking"""
        return ReportService.export_user_csv_enhanced(user_id)
    
    @staticmethod
    def export_admin_csv(requested_by):
        """Export all users' quiz data as CSV for admin"""
        import csv
        import os
        from io import StringIO
        
        try:
            scores = db.session.query(Score, User, Quiz)\
                .join(User, Score.user_id == User.id)\
                .join(Quiz, Score.quiz_id == Quiz.id)\
                .order_by(Score.date_stamp_of_attempt.desc()).all()
            
            if not scores:
                return "No quiz data found"
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Date', 'User Name', 'User Email', 'Quiz Name', 'Subject', 'Chapter',
                'Score', 'Total Marks', 'Percentage', 'Questions Attempted', 
                'Total Questions', 'Status'
            ])
            
            for score, user, quiz in scores:
                subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else 'N/A'
                chapter_name = quiz.chapter.name if quiz.chapter else 'N/A'
                
                writer.writerow([
                    score.date_stamp_of_attempt.strftime('%Y-%m-%d') if score.date_stamp_of_attempt else 'N/A',
                    user.fullname or 'N/A',
                    user.email,
                    quiz.name,
                    subject_name,
                    chapter_name,
                    score.total_score or 0,
                    score.total_marks or 0,
                    f"{(score.total_score / score.total_marks * 100):.1f}%" if score.total_marks > 0 else "0%",
                    score.attempted_questions or 0,
                    score.total_questions or 0,
                    'Completed' if score.time_stamp_of_submited else 'In Progress'
                ])
            
            filename = f"admin_all_users_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('exports', filename)
            
            os.makedirs('exports', exist_ok=True)
            
            with open(filepath, 'w', newline='') as csvfile:
                csvfile.write(output.getvalue())
            
            logger.info(f"Admin CSV export completed by {requested_by}: {filepath}")
            return f"Admin CSV exported successfully: {filepath}"
            
        except Exception as e:
            logger.error(f"Error exporting admin CSV requested by {requested_by}: {str(e)}")
            return f"Export failed: {str(e)}"

    @staticmethod
    def send_monthly_reports_manual():
        """
        Manually send monthly reports to ALL users who have enabled them (bypass scheduling)
        """
        logger.info("Manual monthly reports task started")
        
        active_users = User.query.filter_by(status='active').all()
        
        now = datetime.now()
        if now.day < 15:  
            if now.month == 1:
                report_year = now.year - 1
                report_month = 12
            else:
                report_year = now.year
                report_month = now.month - 1
        else:  
            report_year = now.year
            report_month = now.month
        
        month_str = f"{report_year}-{report_month:02d}"
        
        logger.info(f"Generating manual monthly reports for {month_str}")
        
        report_count = 0
        
        for user in active_users:
            try:
                if user.role == 'admin':
                    continue
                
                user_pref = UserPreference.query.filter_by(user_id=user.id).first()
                if user_pref and not user_pref.receive_monthly:
                    continue
                
                if ReportService._generate_and_send_monthly_report_manual(user, report_year, report_month):
                    report_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing manual monthly report for user {user.id}: {str(e)}")
                continue
        
        result_message = f"Sent {report_count} manual monthly reports for {month_str}"
        logger.info(result_message)
        return result_message

    @staticmethod 
    def _generate_and_send_monthly_report_manual(user, year, month):
        """Generate and send monthly report for a specific user (manual trigger)"""
        try:
            report_data = ReportService._generate_monthly_report_data(user, year, month)
            
            if not report_data:
                logger.info(f"No data to report for user {user.id} for {year}-{month:02d}")
                return False
            
            subject = f"📊 Distributed Assessment Platform - Monthly Activity Report ({year}-{month:02d}) [Manual]"
            
            html_content = ReportService._create_monthly_report_html(user, report_data, year, month)
            
            # Send email
            msg = Message(
                subject=subject,
                sender=("Distributed Assessment Platform", "noreply@assessmentplatform.com"),
                recipients=[user.email],
                html=html_content
            )
            
            mail.send(msg)
            
            logger.info(f"Manual monthly report sent to {user.fullname} ({user.email}) for {year}-{month:02d}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating manual monthly report for user {user.id}: {str(e)}")
            return False
