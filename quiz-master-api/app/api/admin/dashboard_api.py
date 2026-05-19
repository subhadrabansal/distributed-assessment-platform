from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE
from app.extensions import db
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.score import Score
from app.models.answer import Answer
from app.models.question import Question
from app.common.utils import make_response
from sqlalchemy import func, desc, case, and_
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def admin_dashboard():
    return make_response(True, message="Welcome to the admin dashboard"), 200

@dashboard_bp.route('/admin/dashboard/stats', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_admin_dashboard_stats():
    """Get comprehensive admin dashboard statistics"""
    try:
        current_app.logger.info("Admin dashboard stats requested")
        
        # Basic counts
        total_users = User.query.filter_by(role='student').count()
        total_quizzes = Quiz.query.count()
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        total_questions = Question.query.count()
        
        current_app.logger.info(f"Basic counts - Users: {total_users}, Quizzes: {total_quizzes}, Subjects: {total_subjects}")
        
        total_quiz_attempts = Score.query.count()
        completed_attempts = Score.query.filter(Score.time_stamp_of_submited.isnot(None)).count()
        
        active_users = db.session.query(Score.user_id).distinct().count()
        
        avg_score_result = db.session.query(
            func.avg((Score.total_score * 100.0) / Score.total_marks)
        ).filter(
            and_(Score.total_score.isnot(None), Score.total_marks.isnot(None), Score.total_marks > 0)
        ).scalar()
        average_quiz_score = round(float(avg_score_result), 2) if avg_score_result else 0
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_attempts = Score.query.filter(Score.date_stamp_of_attempt >= seven_days_ago).count()
        recent_completions = Score.query.filter(
            and_(Score.date_stamp_of_attempt >= seven_days_ago, Score.time_stamp_of_submited.isnot(None))
        ).count()
        
        stats = {
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_subjects': total_subjects,
            'total_chapters': total_chapters,
            'total_questions': total_questions,
            'total_quiz_attempts': total_quiz_attempts,
            'completed_attempts': completed_attempts,
            'active_users': active_users,
            'average_quiz_score': average_quiz_score,
            'recent_attempts_7d': recent_attempts,
            'recent_completions_7d': recent_completions,
            'completion_rate': round((completed_attempts / total_quiz_attempts * 100), 2) if total_quiz_attempts > 0 else 0,
            'user_engagement_rate': round((active_users / total_users * 100), 2) if total_users > 0 else 0
        }
        
        return make_response(True, data=stats, message="Admin dashboard stats retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting admin dashboard stats: {str(e)}")
        return make_response(False, message="Failed to retrieve dashboard statistics"), 500

@dashboard_bp.route('/admin/dashboard/chart-data', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_admin_chart_data():
    """Get comprehensive chart data for admin dashboard"""
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        user_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago,
            User.role == 'student'
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        quiz_attempts = db.session.query(
            func.date(Score.date_stamp_of_attempt).label('date'),
            func.count(Score.id).label('count')
        ).filter(Score.date_stamp_of_attempt >= thirty_days_ago)\
         .group_by(func.date(Score.date_stamp_of_attempt)).order_by('date').all()
        
        subject_quiz_distribution = []
        all_subjects = Subject.query.all()
        
        for subject in all_subjects:
            quiz_count = db.session.query(func.count(Quiz.id)).join(
                Chapter, Quiz.chapter_id == Chapter.id
            ).filter(Chapter.subject_id == subject.id).scalar() or 0
            
            class SubjectQuizResult:
                def __init__(self, subject_name, quiz_count):
                    self.subject_name = subject_name
                    self.quiz_count = quiz_count
            
            subject_quiz_distribution.append(SubjectQuizResult(subject.name, quiz_count))
        
        score_ranges = [
            ('0-20', 0, 20),
            ('21-40', 21, 40),
            ('41-60', 41, 60),
            ('61-80', 61, 80),
            ('81-100', 81, 100)
        ]
        
        score_distribution = []
        for range_name, min_score, max_score in score_ranges:
            count = Score.query.filter(
                and_(
                    Score.total_score.isnot(None),
                    Score.total_marks.isnot(None),
                    Score.total_marks > 0,
                    (Score.total_score * 100.0 / Score.total_marks) >= min_score,
                    (Score.total_score * 100.0 / Score.total_marks) <= max_score
                )
            ).count()
            score_distribution.append({'range': range_name, 'count': count})
        
        top_users = db.session.query(
            User.fullname,
            func.avg((Score.total_score * 100.0) / Score.total_marks).label('avg_score'),
            func.count(Score.id).label('attempts')
        ).join(Score, User.id == Score.user_id)\
         .filter(
            and_(
                Score.total_score.isnot(None),
                Score.total_marks.isnot(None),
                Score.total_marks > 0
            )
         )\
         .group_by(User.id, User.fullname)\
         .having(func.count(Score.id) >= 1)\
         .order_by(desc('avg_score'))\
         .limit(10).all()
        
        subject_performance = db.session.query(
            Subject.name,
            func.avg((Score.total_score * 100.0) / Score.total_marks).label('avg_score'),
            func.count(Score.id).label('total_attempts')
        ).join(Chapter, Subject.id == Chapter.subject_id)\
         .join(Quiz, Chapter.id == Quiz.chapter_id)\
         .join(Score, Quiz.id == Score.quiz_id)\
         .filter(
            and_(
                Score.total_score.isnot(None),
                Score.total_marks.isnot(None),
                Score.total_marks > 0
            )
         )\
         .group_by(Subject.id, Subject.name)\
         .order_by(desc('avg_score')).all()
        
        
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_completions = db.session.query(
            func.strftime('%Y-%m', Score.time_stamp_of_submited).label('month'),
            func.count(Score.id).label('completions')
        ).filter(
            and_(Score.time_stamp_of_submited >= six_months_ago,
                 Score.time_stamp_of_submited.isnot(None))
        ).group_by(func.strftime('%Y-%m', Score.time_stamp_of_submited))\
         .order_by('month').all()
        
        chart_data = {
            'userRegistrations': [
                {'date': str(reg.date), 'count': reg.count} 
                for reg in user_registrations
            ] if user_registrations else [],
            'quizAttempts': [
                {'date': str(attempt.date), 'count': attempt.count} 
                for attempt in quiz_attempts
            ] if quiz_attempts else [],
            'subjectQuizDistribution': [
                {'subject': dist.subject_name, 'count': dist.quiz_count} 
                for dist in subject_quiz_distribution
            ] if subject_quiz_distribution else [],
            'difficultyDistribution': [],
            'scoreDistribution': score_distribution or [],
            'topUsers': [
                {'name': user.fullname, 'avgScore': round(float(user.avg_score), 2), 'attempts': user.attempts} 
                for user in top_users
            ] if top_users else [],
            'subjectPerformance': [
                {'subject': perf.name, 'avgScore': round(float(perf.avg_score), 2), 'attempts': perf.total_attempts} 
                for perf in subject_performance
            ] if subject_performance else [],
            'monthlyCompletions': [
                {'month': comp.month, 'completions': comp.completions} 
                for comp in monthly_completions
            ] if monthly_completions else []
        }
        
        return make_response(True, data=chart_data, message="Admin chart data retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting admin chart data: {str(e)}")
        return make_response(False, message="Failed to retrieve chart data"), 500

@dashboard_bp.route('/admin/dashboard/recent-activity', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_recent_activity():
    """Get recent system activity for admin dashboard"""
    try:
        recent_attempts = db.session.query(
            Score.id,
            User.fullname.label('user_name'),
            Quiz.name.label('quiz_name'),
            Subject.name.label('subject_name'),
            Score.total_score,
            Score.total_marks,
            Score.date_stamp_of_attempt,
            Score.time_stamp_of_submited
        ).join(User, Score.user_id == User.id)\
         .join(Quiz, Score.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)\
         .order_by(desc(Score.date_stamp_of_attempt))\
         .limit(20).all()
        
        recent_users = User.query.filter_by(role='student')\
                            .order_by(desc(User.created_at))\
                            .limit(10).all()
        
        activity_data = {
            'recentAttempts': [
                {
                    'id': attempt.id,
                    'userName': attempt.user_name,
                    'quizName': attempt.quiz_name,
                    'subject': attempt.subject_name,
                    'score': round((attempt.total_score / attempt.total_marks * 100), 1) if attempt.total_marks and attempt.total_marks > 0 else 0,
                    'startTime': attempt.date_stamp_of_attempt.isoformat() if attempt.date_stamp_of_attempt else None,
                    'endTime': attempt.time_stamp_of_submited.isoformat() if attempt.time_stamp_of_submited else None,
                    'status': 'completed' if attempt.time_stamp_of_submited else 'in_progress'
                }
                for attempt in recent_attempts
            ],
            'recentUsers': [
                {
                    'id': user.id,
                    'name': user.fullname,
                    'email': user.email,
                    'registrationDate': user.created_at.isoformat() if user.created_at else None
                }
                for user in recent_users
            ]
        }
        
        return make_response(True, data=activity_data, message="Recent activity retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent activity: {str(e)}")
        return make_response(False, message="Failed to retrieve recent activity"), 500

@dashboard_bp.route('/admin/dashboard/system-logs', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_system_logs():
    """Get last 100 warning/error logs from the application log file"""
    try:
        import os
        import re
        from datetime import datetime
        
        log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'log', 'app.log')
        
        if not os.path.exists(log_file_path):
            return make_response(True, data={'logs': []}, message="Log file not found")
        
        logs = []
        log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (WARNING|ERROR) - (.+)$'
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                    
                match = re.match(log_pattern, line)
                if match:
                    timestamp_str, logger_name, level, message = match.groups()
                    
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = timestamp_str
                    
                    logs.append({
                        'timestamp': formatted_time,
                        'level': level,
                        'logger': logger_name,
                        'message': message,
                        'severity': 'high' if level == 'ERROR' else 'medium'
                    })
                    
                    if len(logs) >= 100:
                        break
                        
        except Exception as read_error:
            current_app.logger.error(f"Error reading log file: {str(read_error)}")
            return make_response(False, message="Error reading log file"), 500
        
        log_data = {
            'logs': logs,
            'total_count': len(logs),
            'error_count': len([log for log in logs if log['level'] == 'ERROR']),
            'warning_count': len([log for log in logs if log['level'] == 'WARNING'])
        }
        
        return make_response(True, data=log_data, message="System logs retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting system logs: {str(e)}")
        return make_response(False, message="Failed to retrieve system logs"), 500

@dashboard_bp.route('/admin/dashboard/reminder-logs', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_reminder_logs():
    """Get reminder logs from the last 24 hours"""
    try:
        from app.models.notification import ReminderLog
        
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        reminder_logs = ReminderLog.query.filter(
            ReminderLog.sent_at >= twenty_four_hours_ago
        ).order_by(ReminderLog.sent_at.desc()).all()
        
        logs_data = []
        for log in reminder_logs:
            user = User.query.get(log.user_id)
            logs_data.append({
                'id': log.id,
                'user_id': log.user_id,
                'user_name': user.fullname if user else 'Unknown User',
                'user_email': user.email if user else 'Unknown Email',
                'sent_at': log.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                'channel': log.channel,
                'status': log.status,
                'message_preview': log.message[:100] + '...' if log.message and len(log.message) > 100 else log.message or ''
            })
        
        total_sent = len([log for log in reminder_logs if log.status == 'sent'])
        total_failed = len([log for log in reminder_logs if log.status == 'failed'])
        
        result_data = {
            'logs': logs_data,
            'total_count': len(logs_data),
            'sent_count': total_sent,
            'failed_count': total_failed,
            'time_range': '24 hours'
        }
        
        return make_response(True, data=result_data, message="Reminder logs retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting reminder logs: {str(e)}")
        return make_response(False, message="Failed to retrieve reminder logs"), 500

@dashboard_bp.route('/admin/dashboard/report-history', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_report_history():
    """Get report history for the current month"""
    try:
        from app.models.notification import ReportHistory
        
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        report_history = ReportHistory.query.filter(
            ReportHistory.created_at >= start_of_month
        ).order_by(ReportHistory.created_at.desc()).all()
        
        reports_data = []
        for report in report_history:
            user = User.query.get(report.user_id)
            reports_data.append({
                'id': report.id,
                'user_id': report.user_id,
                'user_name': user.fullname if user else 'Unknown User',
                'user_email': user.email if user else 'Unknown Email',
                'report_type': report.report_type,
                'month': report.month,
                'status': report.status,
                'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'filename': report.filename,
                'file_path': report.file_path,
                'task_id': report.task_id,
                'error_message': report.error_message
            })
        
        monthly_reports = [r for r in report_history if r.report_type == 'monthly']
        csv_exports = [r for r in report_history if r.report_type == 'csv_export']
        
        completed_reports = len([r for r in report_history if r.status in ['sent', 'completed']])
        failed_reports = len([r for r in report_history if r.status == 'failed'])
        pending_reports = len([r for r in report_history if r.status in ['pending', 'processing']])
        
        result_data = {
            'reports': reports_data,
            'total_count': len(reports_data),
            'monthly_reports_count': len(monthly_reports),
            'csv_exports_count': len(csv_exports),
            'completed_count': completed_reports,
            'failed_count': failed_reports,
            'pending_count': pending_reports,
            'month_year': now.strftime('%B %Y')
        }
        
        return make_response(True, data=result_data, message="Report history retrieved successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error getting report history: {str(e)}")
        return make_response(False, message="Failed to retrieve report history"), 500