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
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

# Database Schema Reference:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor  # Returns results as dictionaries
    )

@app.route('/api/messages/<int:user_id>', methods=['GET'])
def get_user_messages(user_id):
    """
    Retrieves all messages where the specified user is either the sender or the receiver.
    
    Args:
        user_id (int): The ID of the user to retrieve messages for.
        
    Returns:
        JSON response containing the list of messages or error details.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL Query using parameterized inputs to prevent SQL Injection.
        # We select messages where the user is the sender OR the receiver.
        query = """
            SELECT 
                message_id, 
                sender_id, 
                receiver_id, 
                content, 
                created_at 
            FROM messages 
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY created_at DESC
        """
        
        # Execute the query with the user_id passed twice (once for sender check, once for receiver check)
        cursor.execute(query, (user_id, user_id))
        
        messages = cursor.fetchall()
        
        return jsonify({
            "status": "success",
            "count": len(messages),
            "data": messages
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally here if logging is set up
        return jsonify({
            "status": "error",
            "message": "Database error occurred",
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "details": str(e)
        }), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```