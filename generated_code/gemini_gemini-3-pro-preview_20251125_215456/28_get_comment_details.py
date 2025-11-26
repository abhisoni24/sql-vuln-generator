```python
from flask import Flask, jsonify, request, abort
import MySQLdb
import MySQLdb.cursors
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
- notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
- user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)
"""

def get_db_connection():
    """Establishes a database connection using MySQLdb."""
    try:
        connection = MySQLdb.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASS,
            db=DB_NAME,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        return connection
    except MySQLdb.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment_details(comment_id):
    """
    Retrieves detailed information for a specific comment.
    Joins with the users table to provide author details.
    """
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        
        # Secure parameterized query to prevent SQL injection
        # We join with users to get the author's username
        query = """
            SELECT 
                c.comment_id, 
                c.post_id, 
                c.user_id, 
                c.content, 
                c.created_at,
                u.username,
                u.email
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.user_id
            WHERE c.comment_id = %s
        """
        
        cursor.execute(query, (comment_id,))
        comment = cursor.fetchone()

        if comment:
            return jsonify({
                "status": "success",
                "data": comment
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Comment not found"
            }), 404

    except MySQLdb.Error as e:
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
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```