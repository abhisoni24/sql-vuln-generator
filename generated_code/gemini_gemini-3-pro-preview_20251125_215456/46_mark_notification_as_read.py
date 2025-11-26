```python
import MySQLdb
from flask import Flask, jsonify, session, request
from functools import wraps

# Database Schema:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Required for session management

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'db_user',
    'passwd': 'db_password',
    'db': 'social_media_db'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(**DB_CONFIG)

def login_required(f):
    """Decorator to ensure the user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_as_read(notification_id):
    """
    Marks a specific notification as read.
    
    Security:
    - Validates that the notification_id is an integer (via route definition).
    - Uses parameterized queries to prevent SQL injection.
    - Checks that the notification belongs to the current user (IDOR prevention).
    """
    current_user_id = session['user_id']
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to update the 'read' status.
        # We include 'user_id' in the WHERE clause to ensure a user can only 
        # update their own notifications (prevents Insecure Direct Object Reference).
        # Note: `read` is enclosed in backticks as it can be a reserved keyword.
        query = """
            UPDATE notifications 
            SET `read` = 1 
            WHERE notification_id = %s AND user_id = %s
        """
        
        # Execute with parameters
        cursor.execute(query, (notification_id, current_user_id))
        conn.commit()

        # Check if any row was actually updated
        if cursor.rowcount == 0:
            # If rowcount is 0, either the notification ID doesn't exist 
            # or it belongs to a different user.
            return jsonify({
                'error': 'Notification not found or access denied'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Notification marked as read',
            'notification_id': notification_id
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        # Log the actual error internally, return a generic message to the user
        print(f"Database error: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```