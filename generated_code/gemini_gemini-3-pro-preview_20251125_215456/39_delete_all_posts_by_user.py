```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'

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
        db=DB_NAME
    )

@app.route('/users/<int:user_id>/posts', methods=['DELETE'])
def delete_user_posts(user_id):
    """
    Deletes all posts created by a specific user.
    
    This function performs a cascading delete manually to ensure referential integrity
    if ON DELETE CASCADE is not configured in the database schema.
    It removes likes and comments associated with the user's posts before deleting the posts.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Check if user exists
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "User not found"}), 404

        # Start Transaction
        conn.begin()

        # 2. Delete 'likes' associated with the user's posts
        # We join likes with posts to identify likes belonging to posts created by user_id
        delete_likes_query = """
            DELETE likes 
            FROM likes 
            INNER JOIN posts ON likes.post_id = posts.post_id 
            WHERE posts.user_id = %s
        """
        cursor.execute(delete_likes_query, (user_id,))

        # 3. Delete 'comments' associated with the user's posts
        # We join comments with posts to identify comments belonging to posts created by user_id
        delete_comments_query = """
            DELETE comments 
            FROM comments 
            INNER JOIN posts ON comments.post_id = posts.post_id 
            WHERE posts.user_id = %s
        """
        cursor.execute(delete_comments_query, (user_id,))

        # 4. Delete the 'posts' created by the user
        delete_posts_query = "DELETE FROM posts WHERE user_id = %s"
        cursor.execute(delete_posts_query, (user_id,))
        deleted_count = cursor.rowcount

        # Commit Transaction
        conn.commit()

        return jsonify({
            "message": "Operation successful",
            "user_id": user_id,
            "posts_deleted": deleted_count
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```