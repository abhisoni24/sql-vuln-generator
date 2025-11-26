```python
from flask import Flask, jsonify, abort
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables for credentials
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

# Database Schema Reference:
# users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """
    Retrieves all comments for a specific post_id.
    
    Args:
        post_id (int): The ID of the post to retrieve comments for.
        
    Returns:
        JSON response containing the list of comments or an error message.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to retrieve comments.
        # We join with the 'users' table to provide the username of the commenter,
        # which is standard requirement for displaying comments.
        # Parameterized query (%s) is used to prevent SQL Injection.
        query = """
            SELECT 
                c.comment_id, 
                c.post_id, 
                c.user_id, 
                u.username, 
                c.content, 
                c.created_at
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """
        
        cursor.execute(query, (post_id,))
        comments = cursor.fetchall()

        # Return empty list if no comments found, rather than 404, 
        # as the resource (the list of comments) exists but is empty.
        return jsonify({
            "status": "success",
            "count": len(comments),
            "data": comments
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error in a real application
        return jsonify({
            "status": "error", 
            "message": "Database error occurred."
        }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": "An internal server error occurred."
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