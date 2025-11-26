```python
import MySQLdb
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'

# ==========================================
# Database Schema Reference
# ==========================================
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
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    """
    Adds a new comment to a post.
    
    Expected JSON Payload:
    {
        "post_id": 123,
        "user_id": 456,
        "content": "This is a comment."
    }
    """
    # Get JSON data from request
    data = request.get_json()

    # 1. Input Validation
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON payload"}), 400

    post_id = data.get('post_id')
    user_id = data.get('user_id')
    content = data.get('content')

    # Validate presence of parameters
    if not all([post_id, user_id, content]):
        return jsonify({"success": False, "error": "Missing required parameters: post_id, user_id, content"}), 400

    # Validate content is not empty
    if not isinstance(content, str) or not content.strip():
        return jsonify({"success": False, "error": "Content cannot be empty"}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Check Referential Integrity (Optional but recommended for specific error messages)
        # Check if User exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "User not found"}), 404

        # Check if Post exists
        cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Post not found"}), 404

        # 3. Insert the Comment
        # Using parameterized queries (%s) to prevent SQL Injection
        insert_query = """
            INSERT INTO comments (post_id, user_id, content, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (post_id, user_id, content.strip()))
        
        # Commit the transaction
        conn.commit()
        
        # Get the ID of the newly created comment
        new_comment_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Comment added successfully",
            "data": {
                "comment_id": new_comment_id,
                "post_id": post_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
        }), 201

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        # Log the specific error internally, return generic error to user
        print(f"Database Error: {e}")
        return jsonify({"success": False, "error": "Database operation failed"}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Server Error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    finally:
        # 4. Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```