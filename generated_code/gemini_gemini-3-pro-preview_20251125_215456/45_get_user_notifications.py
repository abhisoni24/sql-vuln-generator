```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables for credentials
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

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
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    """
    Retrieves a list of notifications for a specific user.
    
    Parameters:
        user_id (int): The ID of the user to retrieve notifications for.
        
    Returns:
        JSON response containing the list of notifications or an error message.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Check if user exists (Optional, but good for 404 accuracy)
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        # 2. Retrieve notifications
        # Using parameterized queries (%s) to prevent SQL Injection
        # Quoting `read` as it can be a reserved keyword in some contexts
        query = """
            SELECT 
                notification_id, 
                type, 
                message, 
                `read`, 
                created_at 
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()

        # 3. Format data for JSON response
        notifications = []
        for row in results:
            notifications.append({
                "notification_id": row['notification_id'],
                "type": row['type'],
                "message": row['message'],
                "read": bool(row['read']),
                # Convert datetime object to ISO format string for JSON serialization
                "created_at": row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']
            })

        return jsonify({
            "user_id": user_id,
            "count": len(notifications),
            "notifications": notifications
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally
        print(f"Database Error: {e}")
        return jsonify({"error": "An error occurred while accessing the database"}), 500
        
    except Exception as e:
        # Catch generic errors
        print(f"Server Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
        
    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```