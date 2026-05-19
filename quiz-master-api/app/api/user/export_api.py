from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.notification import ReportHistory
from app.extensions import db
import os
import json
import logging

logger = logging.getLogger(__name__)

user_export_bp = Blueprint('user_export', __name__)

@user_export_bp.route('/trigger-csv-export', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def trigger_csv_export():
    """Trigger CSV export for the current user only"""
    try:
        # Handle OPTIONS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        current_user_identity = get_jwt_identity()
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Create report history entry for this user's export
        from datetime import datetime
        report = ReportHistory(
            user_id=user_id,
            report_type='csv_export',
            status='pending',
            filename=f'user_{user_id}_quiz_report_pending.csv',
            month=datetime.now().strftime('%Y-%m')  # Set current month for CSV export
        )
        
        from app.extensions import db
        db.session.add(report)
        db.session.commit()
        
        # Trigger async CSV export task for this user only
        from app.celery_tasks import export_user_csv
        task = export_user_csv.delay(user_id, report.id)
        
        # Update report with task ID
        report.task_id = task.id
        db.session.commit()
        
        logger.info(f"CSV export triggered for user {user_id}, report ID: {report.id}")
        
        return jsonify({
            'success': True,
            'message': 'CSV export started',
            'export_id': report.id,
            'task_id': task.id,
            'status': 'pending'
        })
        
    except Exception as e:
        logger.error(f"Error triggering CSV export for user: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to trigger CSV export'
        }), 500

@user_export_bp.route('/export-status/<int:export_id>', methods=['GET'])
@jwt_required()
def get_export_status(export_id):
    """Get status of a CSV export"""
    try:
        current_user_identity = get_jwt_identity()
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        export_record = ReportHistory.query.filter_by(
            id=export_id,
            user_id=user_id,
            report_type='csv_export'
        ).first()
        
        if not export_record:
            return jsonify({'error': 'Export not found'}), 404
        
        response_data = {
            'export_id': export_record.id,
            'status': export_record.status,
            'created_at': export_record.created_at.isoformat(),
        }
        
        # If completed, add download info
        if export_record.status == 'completed':
            filename = f"user_{user_id}_quiz_report_{export_record.created_at.strftime('%Y%m%d_%H%M%S')}.csv"
            # Use correct path to exports directory (go up 4 levels from this file)
            exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'exports')
            filepath = os.path.join(exports_dir, filename)
            
            if os.path.exists(filepath):
                response_data['download_url'] = f'/api/user/export/download/{filename}'
                response_data['file_size'] = os.path.getsize(filepath)
                response_data['filename'] = filename
            else:
                response_data['status'] = 'failed'
                response_data['error'] = 'Export file not found'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get export status: {str(e)}'
        }), 500

# Handle undefined export_id gracefully
@user_export_bp.route('/export-status/undefined', methods=['GET'])
@jwt_required()
def get_export_status_undefined():
    """Handle requests with undefined export_id"""
    return jsonify({'error': 'Invalid export ID: undefined'}), 400

@user_export_bp.route('/my-exports', methods=['GET'])
@jwt_required()
def get_my_exports():
    """Get list of user's CSV exports"""
    try:
        current_user_identity = get_jwt_identity()
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        exports = ReportHistory.query.filter_by(
            user_id=user_id,
            report_type='csv_export'
        ).order_by(ReportHistory.created_at.desc()).limit(10).all()
        
        export_list = []
        for export in exports:
            export_data = {
                'export_id': export.id,
                'status': export.status,
                'created_at': export.created_at.isoformat(),
                'month': export.month
            }
            
            # Add download info if completed
            if export.status == 'completed':
                filename = f"user_{user_id}_quiz_report_{export.created_at.strftime('%Y%m%d_%H%M%S')}.csv"
                # Use correct path to exports directory (go up 4 levels from this file)
                exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'exports')
                filepath = os.path.join(exports_dir, filename)
                
                if os.path.exists(filepath):
                    export_data['download_url'] = f'/api/user/export/download/{filename}'
                    export_data['file_size'] = os.path.getsize(filepath)
                    export_data['filename'] = filename
            
            export_list.append(export_data)
        
        return jsonify({'exports': export_list}), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get exports: {str(e)}'
        }), 500

@user_export_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_export_file(filename):
    """Download a CSV export file"""
    try:
        from flask import send_file
        
        current_user_identity = get_jwt_identity()
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        # Security check - only allow CSV files
        if not filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check if user owns this file
        if not filename.startswith(f'user_{user_id}_'):
            return jsonify({'error': 'Permission denied'}), 403
        
        # Use correct path to exports directory (go up 4 levels from this file)
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'exports')
        filepath = os.path.join(exports_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': f'File not found: {filepath}'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to download file: {str(e)}'
        }), 500
