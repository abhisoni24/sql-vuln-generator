```python
from flask import Flask, jsonify, session, request
import MySQLdb
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = 'password'
DB_NAME = 'social_media_db'

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
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)

def login_required(f):
    """Mock decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, check if 'user_id' is in session
        # For demonstration, we assume a user with ID 1 is logged in
        if 'user_id' not in session:
            session['user_id'] = 1 
        return f(*args, **kwargs)
    return decorated_function

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """
    Deletes a post and its associated data (comments, likes).
    Ensures the user requesting the delete is the owner of the post.
    """
    conn = None
    cursor = None
    current_user_id = session.get('user_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Security Check: Verify post existence and ownership
        # Using parameterized query to prevent SQL Injection
        check_query = "SELECT user_id FROM posts WHERE post_id = %s"
        cursor.execute(check_query, (post_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Post not found"}), 404

        post_owner_id = result[0]

        if post_owner_id != current_user_id:
            return jsonify({"error": "Unauthorized: You can only delete your own posts"}), 403

        # 2. Delete Operation
        # We manually delete related records (likes, comments) to ensure functionality
        # even if ON DELETE CASCADE is not configured in the database schema.
        
        # Delete likes associated with the post
        cursor.execute("DELETE FROM likes WHERE post_id = %s", (post_id,))
        
        # Delete comments associated with the post
        cursor.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
        
        # Delete the post itself
        cursor.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))

        # 3. Commit Transaction
        conn.commit()

        return jsonify({"message": "Post and associated data deleted successfully", "post_id": post_id}), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```