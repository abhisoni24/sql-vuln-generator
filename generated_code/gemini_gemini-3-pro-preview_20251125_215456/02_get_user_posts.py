```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

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

# Configuration (should be loaded from environment variables in production)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor  # Returns results as dictionaries
    )

@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """
    Retrieve all posts created by a specific user.
    
    Args:
        user_id (int): The ID of the user retrieved from the URL path.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Validate if user exists (Optional but recommended for 404 handling)
        user_check_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(user_check_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({
                "error": "Not Found",
                "message": f"User with ID {user_id} does not exist."
            }), 404

        # 2. Retrieve posts
        # Using parameterized queries (%s) to prevent SQL Injection
        posts_query = """
            SELECT post_id, user_id, content, created_at 
            FROM posts 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        cursor.execute(posts_query, (user_id,))
        posts = cursor.fetchall()

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "count": len(posts),
            "posts": posts
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally
        print(f"Database Error: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while accessing the database."
        }), 500

    except Exception as e:
        # Handle unexpected errors
        print(f"General Error: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
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