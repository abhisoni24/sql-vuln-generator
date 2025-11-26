```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
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
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates the content of a specific post.
    Expects JSON payload: { "user_id": <int>, "content": <str> }
    
    Note: In a production environment, 'user_id' should be derived from 
    a secure session or JWT token, not the request body.
    """
    conn = None
    cursor = None
    
    try:
        # 1. Validate Request Data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        new_content = data.get('content')
        requester_id = data.get('user_id')

        if not new_content or not isinstance(new_content, str):
            return jsonify({"error": "Content is required and must be text"}), 400
        
        if not requester_id:
            return jsonify({"error": "User ID is required for authorization"}), 401

        # 2. Connect to Database
        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Check if post exists and verify ownership
        # We select the owner of the post to ensure the requester has permission
        check_query = "SELECT user_id FROM posts WHERE post_id = %s"
        cursor.execute(check_query, (post_id,))
        post = cursor.fetchone()

        if not post:
            return jsonify({"error": "Post not found"}), 404

        if post['user_id'] != requester_id:
            return jsonify({"error": "Unauthorized: You can only edit your own posts"}), 403

        # 4. Update the post content
        update_query = "UPDATE posts SET content = %s WHERE post_id = %s"
        cursor.execute(update_query, (new_content, post_id))
        conn.commit()

        return jsonify({
            "message": "Post updated successfully",
            "post_id": post_id
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
    finally:
        # 5. Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```