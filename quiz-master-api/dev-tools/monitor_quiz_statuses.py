#!/usr/bin/env python3
"""
Comprehensive quiz status monitoring and auto-update service
This should be run periodically to ensure quiz statuses are always current
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.quiz import Quiz
from app.extensions import db
from datetime import datetime
import logging

def setup_logging():
    """Setup logging for status updates"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dev-tools/log/quiz_status_updates.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def monitor_and_update_quiz_statuses():
    """Monitor and update quiz statuses with detailed logging"""
    logger = setup_logging()
    app = create_app()
    
    with app.app_context():
        logger.info("🔍 Starting quiz status check...")
        
        quizzes = Quiz.query.all()
        now = datetime.now()
        
        status_counts = {'upcoming': 0, 'ongoing': 0, 'completed': 0, 'updated': 0}
        
        for quiz in quizzes:
            old_status = quiz.status
            
            if now < quiz.start_date:
                correct_status = 'upcoming'
            elif quiz.start_date <= now <= quiz.end_date:
                correct_status = 'ongoing'
            elif now > quiz.end_date:
                correct_status = 'completed'
            else:
                continue
            
            status_counts[correct_status] += 1
            
            if old_status != correct_status:
                quiz.status = correct_status
                quiz.updated_at = now
                status_counts['updated'] += 1
                
                logger.info(f"📅 Quiz {quiz.id} '{quiz.name}' status updated: {old_status} → {correct_status}")
                
                days_since_start = (now - quiz.start_date).days
                days_until_end = (quiz.end_date - now).days
                logger.info(f"   Start: {quiz.start_date} ({days_since_start} days ago)")
                logger.info(f"   End: {quiz.end_date} ({days_until_end} days remaining)")
        
        if status_counts['updated'] > 0:
            try:
                db.session.commit()
                logger.info(f"✅ Updated {status_counts['updated']} quiz statuses successfully")
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ Error updating quiz statuses: {e}")
        
        # Log summary
        logger.info(f"📊 Quiz Status Summary:")
        logger.info(f"   Upcoming: {status_counts['upcoming']}")
        logger.info(f"   Ongoing: {status_counts['ongoing']}")
        logger.info(f"   Completed: {status_counts['completed']}")
        logger.info(f"   Updated: {status_counts['updated']}")
        
        return status_counts

def check_status_transitions():
    """Check for quizzes that will transition status soon"""
    logger = setup_logging()
    app = create_app()
    
    with app.app_context():
        logger.info("🔮 Checking upcoming status transitions...")
        
        quizzes = Quiz.query.all()
        now = datetime.now()
        
        for quiz in quizzes:
            hours_until_start = (quiz.start_date - now).total_seconds() / 3600
            if 0 < hours_until_start <= 24 and quiz.status == 'upcoming':
                logger.info(f"⏰ Quiz {quiz.id} '{quiz.name}' starts in {hours_until_start:.1f} hours")
            
            hours_until_end = (quiz.end_date - now).total_seconds() / 3600
            if 0 < hours_until_end <= 24 and quiz.status == 'ongoing':
                logger.info(f"⏰ Quiz {quiz.id} '{quiz.name}' ends in {hours_until_end:.1f} hours")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "transitions":
        check_status_transitions()
    else:
        result = monitor_and_update_quiz_statuses()
        
        if len(sys.argv) == 1:
            check_status_transitions()
