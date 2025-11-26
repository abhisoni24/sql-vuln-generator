```python
from flask import Flask, jsonify, request, g
import MySQLdb
from functools import wraps

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'social_media_db'

"""
Database Schema:
- users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
- posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
- followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
- messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
- notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
- user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)
"""

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )

# Mock authentication decorator for demonstration purposes
# In a real app, this would verify a session or JWT token
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simulating a logged-in user with ID 1
        g.user_id = 1 
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """
    Deletes a specific notification.
    
    Security: 
    - Ensures the notification belongs to the currently logged-in user (prevents IDOR).
    - Uses parameterized queries to prevent SQL Injection.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Secure deletion: We include user_id in the WHERE clause.
        # This ensures a user can only delete their own notifications.
        query = "DELETE FROM notifications WHERE notification_id = %s AND user_id = %s"
        
        # Execute with parameters
        cursor.execute(query, (notification_id, g.user_id))
        conn.commit()

        # Check if any row was actually deleted
        if cursor.rowcount == 0:
            # If 0, either the notification doesn't exist OR it belongs to another user
            return jsonify({
                "status": "error", 
                "message": "Notification not found or access denied"
            }), 404

        return jsonify({
            "status": "success", 
            "message": f"Notification {notification_id} deleted successfully"
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({
            "status": "error", 
            "message": "Database error occurred", 
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": "An unexpected error occurred", 
            "details": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```