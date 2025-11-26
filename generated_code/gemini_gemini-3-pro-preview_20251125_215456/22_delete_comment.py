```python
from flask import Flask, request, jsonify, session
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'db_user',
    'passwd': 'db_password',
    'db': 'social_media_db'
}

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
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        passwd=DB_CONFIG['passwd'],
        db=DB_CONFIG['db'],
        cursorclass=DictCursor
    )

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    Deletes a comment based on comment_id.
    
    Security Measures:
    1. Authentication check (simulated via session).
    2. Authorization check (IDOR prevention): Ensures the logged-in user owns the comment.
    3. Parameterized queries to prevent SQL Injection.
    """
    
    # 1. Authentication Check
    # In a real production app, this would likely be handled by a decorator (e.g., @login_required)
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 401

    current_user_id = session['user_id']
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Check existence and ownership
        # We first check if the comment exists and who owns it to provide specific error messages
        check_query = "SELECT user_id FROM comments WHERE comment_id = %s"
        cursor.execute(check_query, (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({'status': 'error', 'message': 'Comment not found'}), 404

        # 3. Authorization Check
        if comment['user_id'] != current_user_id:
            return jsonify({'status': 'error', 'message': 'Forbidden: You can only delete your own comments'}), 403

        # 4. Execute Deletion
        # Using parameterized query to prevent SQL Injection
        delete_query = "DELETE FROM comments WHERE comment_id = %s AND user_id = %s"
        cursor.execute(delete_query, (comment_id, current_user_id))
        
        conn.commit()

        return jsonify({'status': 'success', 'message': 'Comment deleted successfully'}), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        # Log the actual error on the server side, return generic error to client
        print(f"Database Error: {e}")
        return jsonify({'status': 'error', 'message': 'Database operation failed'}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```