```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables for credentials
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

"""
Database Schema Reference:
- users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
- posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
- followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
- messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
- notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), `read` (BOOLEAN), created_at (DATETIME)
- user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)
"""

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    connection = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )
    return connection

@app.route('/notifications', methods=['POST'])
def create_notification():
    """
    Creates a new notification for a specific user.
    
    Expected JSON payload:
    {
        "user_id": int,
        "type": str,
        "message": str
    }
    """
    connection = None
    cursor = None
    
    try:
        # 1. Validate Input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        user_id = data.get('user_id')
        notif_type = data.get('type')
        message = data.get('message')

        if not all([user_id, notif_type, message]):
            return jsonify({"error": "Missing required fields: user_id, type, message"}), 400

        if not isinstance(user_id, int):
            return jsonify({"error": "user_id must be an integer"}), 400

        # 2. Connect to Database
        connection = get_db_connection()
        cursor = connection.cursor()

        # 3. Check if User Exists (Referential Integrity)
        # Although Foreign Keys handle this, checking explicitly allows for a cleaner 404 error
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        # 4. Insert Notification
        # We explicitly set `read` to 0 (False) and created_at to NOW()
        # Using parameterized queries (%s) to prevent SQL Injection
        insert_query = """
            INSERT INTO notifications (user_id, type, message, `read`, created_at)
            VALUES (%s, %s, %s, 0, NOW())
        """
        
        cursor.execute(insert_query, (user_id, notif_type, message))
        connection.commit()
        
        new_notification_id = cursor.lastrowid

        return jsonify({
            "message": "Notification created successfully",
            "notification_id": new_notification_id,
            "user_id": user_id,
            "type": notif_type
        }), 201

    except MySQLdb.Error as e:
        if connection:
            connection.rollback()
        # Log the actual error in a real app
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
    finally:
        # 5. Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```