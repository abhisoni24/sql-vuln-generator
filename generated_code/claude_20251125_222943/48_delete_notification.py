```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

notifications_bp = Blueprint('notifications', __name__)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db',
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        raise Exception(f"Database connection error: {str(e)}")

@notifications_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    Delete a specific notification for the authenticated user
    
    Args:
        notification_id (int): ID of the notification to delete
    
    Returns:
        JSON response indicating success or failure
    """
    current_user_id = get_jwt_identity()
    
    if not notification_id:
        raise BadRequest("Notification ID is required")
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify notification belongs to current user
        cursor.execute("""
            SELECT notification_id 
            FROM notifications 
            WHERE notification_id = %s AND user_id = %s
        """, (notification_id, current_user_id))
        
        notification = cursor.fetchone()
        
        if not notification:
            return jsonify({
                "error": "Notification not found or unauthorized",
                "status": "error"
            }), 404
        
        # Delete the notification
        cursor.execute("""
            DELETE FROM notifications 
            WHERE notification_id = %s AND user_id = %s
        """, (notification_id, current_user_id))
        
        conn.commit()
        
        return jsonify({
            "message": "Notification deleted successfully",
            "status": "success"
        }), 200
    
    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }), 500
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 400
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```