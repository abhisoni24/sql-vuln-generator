```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import MySQLdb
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username', 
            passwd='your_password',
            db='social_media_db',
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return None

@notifications_bp.route('/mark_notification_read', methods=['POST'])
@jwt_required()
def mark_notification_read():
    try:
        # Get current user's ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get notification ID from request
        notification_id = request.json.get('notification_id')
        
        # Validate input
        if not notification_id:
            return jsonify({
                'error': 'Notification ID is required',
                'status': 400
            }), 400
        
        # Establish database connection
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'error': 'Database connection failed',
                'status': 500
            }), 500
        
        cursor = connection.cursor()
        
        # First verify notification belongs to current user
        cursor.execute("""
            SELECT user_id FROM notifications 
            WHERE notification_id = %s AND user_id = %s
        """, (notification_id, current_user_id))
        
        notification = cursor.fetchone()
        
        if not notification:
            connection.close()
            return jsonify({
                'error': 'Notification not found or unauthorized',
                'status': 403
            }), 403
        
        # Mark notification as read
        cursor.execute("""
            UPDATE notifications 
            SET read = TRUE 
            WHERE notification_id = %s
        """, (notification_id,))
        
        connection.commit()
        connection.close()
        
        return jsonify({
            'message': 'Notification marked as read',
            'status': 200
        }), 200
    
    except MySQLdb.Error as db_error:
        print(f"Database error: {db_error}")
        return jsonify({
            'error': 'Database operation failed',
            'status': 500
        }), 500
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500
```