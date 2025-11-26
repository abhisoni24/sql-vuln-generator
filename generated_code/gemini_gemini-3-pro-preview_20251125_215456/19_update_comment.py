```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error

app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'db': 'your_database'
}

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

@app.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """
    Updates a comment's content.
    Requires JSON body: {"user_id": <int>, "content": <str>}
    """
    conn = None
    cursor = None
    try:
        # 1. Input Validation
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        new_content = data.get('content')
        user_id = data.get('user_id') # In a real app, this would come from the session/token

        if not new_content or not isinstance(new_content, str):
            return jsonify({"error": "Content is required and must be a string"}), 400
        
        if not user_id or not isinstance(user_id, int):
            return jsonify({"error": "Valid User ID is required for authorization"}), 400

        # 2. Database Connection
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()

        # 3. Secure Update Operation
        # We include user_id in the WHERE clause to ensure the user owns the comment (Authorization)
        # We use parameterized queries (%s) to prevent SQL Injection
        query = "UPDATE comments SET content = %s WHERE comment_id = %s AND user_id = %s"
        params = (new_content, comment_id, user_id)
        
        cursor.execute(query, params)
        conn.commit()

        # 4. Check if update was successful
        if cursor.rowcount == 0:
            # Row count 0 implies either comment_id doesn't exist OR user_id doesn't match (Unauthorized)
            return jsonify({"error": "Comment not found or unauthorized access"}), 404

        return jsonify({
            "message": "Comment updated successfully",
            "comment_id": comment_id
        }), 200

    except Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```