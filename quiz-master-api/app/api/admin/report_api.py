from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.common.role_utils import roles_required
import os

report_bp = Blueprint('report', __name__)

@report_bp.route('/trigger-monthly-reports', methods=['POST'])
@jwt_required()
@roles_required('admin')
def trigger_monthly_reports():
    """Manually trigger monthly reports generation"""
    try:
        from app.celery_tasks import send_monthly_reports
        
        task = send_monthly_reports.delay()
        
        return jsonify({
            'message': 'Monthly reports task triggered successfully',
            'task_id': task.id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to trigger monthly reports: {str(e)}'
        }), 500

@report_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def export_user_data():
    """Export current user's quiz data as CSV"""
    try:
        from app.celery_tasks import export_user_csv
        
        current_user_id = get_jwt_identity()
        
        task = export_user_csv.delay(current_user_id)
        
        return jsonify({
            'message': 'CSV export task triggered successfully',
            'task_id': task.id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to trigger CSV export: {str(e)}'
        }), 500

@report_bp.route('/export-all-csv', methods=['POST'])
@jwt_required()
@roles_required('admin')
def export_all_data():
    """Export all users' quiz data as CSV (admin only)"""
    try:
        from app.celery_tasks import export_admin_csv
        
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        task = export_admin_csv.delay(current_user.email)
        
        return jsonify({
            'message': 'Admin CSV export task triggered successfully',
            'task_id': task.id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to trigger admin CSV export: {str(e)}'
        }), 500

@report_bp.route('/list-exports', methods=['GET'])
@jwt_required()
def list_exports():
    """List available export files"""
    try:
        exports_dir = 'exports'
        if not os.path.exists(exports_dir):
            return jsonify({'files': []}), 200
        
        files = []
        for filename in os.listdir(exports_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(exports_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'download_url': f'/api/report/download/{filename}'
                })
        
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to list exports: {str(e)}'
        }), 500

@report_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_export(filename):
    """Download an export file"""
    try:
        from flask import send_file
        
        if not filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = os.path.join('exports', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin' and not filename.startswith(f'user_{current_user_id}_'):
            return jsonify({'error': 'Permission denied'}), 403
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to download file: {str(e)}'
        }), 500
