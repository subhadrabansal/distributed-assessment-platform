"""
Quiz Status Management Utility
Centralized functions for updating quiz statuses based on date/time
"""

from app.models.quiz import Quiz
from app.common.enums import QUIZ_STATUSES
from app.extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuizStatusManager:
    
    @staticmethod
    def update_all_quiz_statuses(context='manual'):
        """
        Update all quiz statuses based on current date/time
        
        Args:
            context (str): Context of the update ('login', 'manual', 'scheduled', etc.)
        
        Returns:
            dict: Update results with counts and details
        """
        try:
            now = datetime.now()
            quizzes = Quiz.query.all()
            
            results = {
                'total_quizzes': len(quizzes),
                'updated_count': 0,
                'updates': [],
                'errors': [],
                'context': context
            }
            
            for quiz in quizzes:
                try:
                    old_status = quiz.status
                    new_status = QuizStatusManager._determine_quiz_status(quiz, now)
                    
                    
                    if old_status != new_status and old_status != 'cancelled':
                        quiz.status = new_status
                        quiz.updated_at = now
                        results['updated_count'] += 1
                        
                        update_info = {
                            'quiz_id': quiz.id,
                            'quiz_name': quiz.name,
                            'old_status': old_status,
                            'new_status': new_status,
                            'start_date': quiz.start_date,
                            'end_date': quiz.end_date
                        }
                        results['updates'].append(update_info)
                        
                        logger.info(f"Quiz {quiz.id} '{quiz.name}' status updated ({context}): {old_status} → {new_status}")
                        
                except Exception as e:
                    error_info = {
                        'quiz_id': quiz.id if hasattr(quiz, 'id') else 'unknown',
                        'error': str(e)
                    }
                    results['errors'].append(error_info)
                    logger.error(f"Error updating quiz {quiz.id}: {e}")
            
            # Commit all changes
            if results['updated_count'] > 0:
                db.session.commit()
                logger.info(f"Successfully updated {results['updated_count']} quiz statuses ({context})")
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error in update_all_quiz_statuses ({context}): {e}")
            db.session.rollback()
            return {
                'total_quizzes': 0,
                'updated_count': 0,
                'updates': [],
                'errors': [{'error': str(e)}],
                'context': context
            }
    
    @staticmethod
    def _determine_quiz_status(quiz, current_time=None):
        """
        Determine the correct status for a quiz based on its dates
        
        Args:
            quiz: Quiz object
            current_time: Optional datetime, defaults to now()
        
        Returns:
            str: The correct status ('upcoming', 'ongoing', 'completed')
        """
        if current_time is None:
            current_time = datetime.now()
        
        if current_time < quiz.start_date:
            return QUIZ_STATUSES[0]  
        elif quiz.start_date <= current_time <= quiz.end_date:
            return QUIZ_STATUSES[1]  
        elif current_time > quiz.end_date:
            return QUIZ_STATUSES[2]  
        else:
            return quiz.status  
    
    @staticmethod
    def update_single_quiz_status(quiz_id, context='manual'):
        """
        Update status for a single quiz
        
        Args:
            quiz_id (int): Quiz ID to update
            context (str): Context of the update
        
        Returns:
            dict: Update result
        """
        try:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'success': False, 'error': f'Quiz {quiz_id} not found'}
            
            old_status = quiz.status
            new_status = QuizStatusManager._determine_quiz_status(quiz)
            
            if old_status != new_status and old_status != 'cancelled':
                quiz.status = new_status
                quiz.updated_at = datetime.now()
                db.session.commit()
                
                logger.info(f"Quiz {quiz_id} status updated ({context}): {old_status} → {new_status}")
                
                return {
                    'success': True,
                    'quiz_id': quiz_id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'updated': True
                }
            else:
                return {
                    'success': True,
                    'quiz_id': quiz_id,
                    'old_status': old_status,
                    'new_status': old_status,
                    'updated': False
                }
                
        except Exception as e:
            logger.error(f"Error updating quiz {quiz_id} status: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_quiz_status_summary():
        """
        Get a summary of all quiz statuses
        
        Returns:
            dict: Status counts and details
        """
        try:
            quizzes = Quiz.query.all()
            now = datetime.now()
            
            summary = {
                'total': len(quizzes),
                'upcoming': 0,
                'ongoing': 0,
                'completed': 0,
                'cancelled': 0,
                'status_mismatches': [],
                'upcoming_transitions': [],
                'ending_soon': []
            }
            
            for quiz in quizzes:
                summary[quiz.status] += 1
                
                expected_status = QuizStatusManager._determine_quiz_status(quiz, now)
                if quiz.status != expected_status and quiz.status != 'cancelled':
                    summary['status_mismatches'].append({
                        'quiz_id': quiz.id,
                        'quiz_name': quiz.name,
                        'current_status': quiz.status,
                        'expected_status': expected_status
                    })
                
                hours_until_start = (quiz.start_date - now).total_seconds() / 3600
                if 0 < hours_until_start <= 24 and quiz.status == 'upcoming':
                    summary['upcoming_transitions'].append({
                        'quiz_id': quiz.id,
                        'quiz_name': quiz.name,
                        'starts_in_hours': round(hours_until_start, 1)
                    })
                
                hours_until_end = (quiz.end_date - now).total_seconds() / 3600
                if 0 < hours_until_end <= 24 and quiz.status == 'ongoing':
                    summary['ending_soon'].append({
                        'quiz_id': quiz.id,
                        'quiz_name': quiz.name,
                        'ends_in_hours': round(hours_until_end, 1)
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting quiz status summary: {e}")
            return {'error': str(e)}
