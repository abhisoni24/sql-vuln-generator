```python
from flask import Blueprint, request, jsonify
import MySQLdb
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

notifications_bp = Blueprint('notifications', __name__)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_network_db',
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return None

@notifications_bp.route('/notifications/create', methods=['POST'])
@jwt_required()
def create_notification():
    try:
        # Validate input parameters
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['user_id', 'type', 'message']):
            return jsonify({
                'error': 'Missing required parameters', 
                'status': 400
            }), 400
        
        # Extract parameters
        user_id = data['user_id']
        notification_type = data['type']
        message = data['message']
        
        # Validate user_id exists
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'error': 'Database connection failed', 
                'status': 500
            }), 500
        
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({
                'error': 'User does not exist', 
                'status': 404
            }), 404
        
        # Insert notification
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO notifications 
            (user_id, type, message, read, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, notification_type, message, False, current_time))
        
        # Get the ID of the newly created notification
        notification_id = cursor.lastrowid
        
        # Commit transaction
        conn.commit()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Notification created successfully',
            'notification_id': notification_id,
            'status': 201
        }), 201
    
    except MySQLdb.Error as db_error:
        # Rollback in case of database error
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        
        return jsonify({
            'error': f'Database error: {str(db_error)}', 
            'status': 500
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}', 
            'status': 500
        }), 500
```

Key Security and Functional Features:
1. JWT authentication with `@jwt_required()`
2. Comprehensive error handling
3. Input validation
4. Secure database connection management
5. Transaction handling with commit/rollback
6. Prevents SQL injection via parameterized queries
7. Validates user existence before creating notification
8. Returns appropriate HTTP status codes
9. Logs and handles various potential error scenarios

Note: Replace placeholders for database connection details with your actual credentials.