```python
from flask import Flask, jsonify, request
import MySQLdb
import os

app = Flask(__name__)

# Database Schema:
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
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        passwd=os.getenv('DB_PASS', 'password'),
        db=os.getenv('DB_NAME', 'social_app')
    )

@app.route('/users/<int:user_id>/comments', methods=['DELETE'])
def delete_all_user_comments(user_id):
    """
    Deletes all comments created by a specific user.
    
    Args:
        user_id (int): The ID of the user whose comments are to be deleted.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optional: Check if user exists first to return 404 if invalid user
        # This step depends on specific API requirements, but is good practice.
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "User not found"}), 404

        # Securely delete comments using parameterized query to prevent SQL Injection
        delete_query = "DELETE FROM comments WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))
        
        deleted_count = cursor.rowcount
        conn.commit()

        return jsonify({
            "message": "Comments deleted successfully",
            "user_id": user_id,
            "deleted_count": deleted_count
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        # Log the error in a real application
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```