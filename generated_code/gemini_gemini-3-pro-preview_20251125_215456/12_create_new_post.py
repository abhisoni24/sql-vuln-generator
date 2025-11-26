```python
from flask import Flask, request, jsonify
import MySQLdb
from datetime import datetime

app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database_name'
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

@app.route('/create_post', methods=['POST'])
def create_post():
    """
    Endpoint to create a new post for a user.
    Expected JSON payload:
    {
        "user_id": int,
        "content": str
    }
    """
    # 1. Validate Input
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
        
    user_id = data.get('user_id')
    content = data.get('content')

    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "Invalid or missing user_id"}), 400
    
    if not content or not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Content cannot be empty"}), 400

    conn = None
    cursor = None

    try:
        # 2. Connect to Database
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()

        # 3. Check if user exists (Optional, but provides better error messages than FK constraint failure)
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "User not found"}), 404

        # 4. Insert Post
        # Using parameterized queries (%s) to prevent SQL Injection
        insert_query = """
            INSERT INTO posts (user_id, content, created_at) 
            VALUES (%s, %s, %s)
        """
        current_time = datetime.now()
        cursor.execute(insert_query, (user_id, content, current_time))
        
        conn.commit()
        
        # Get the ID of the newly created post
        new_post_id = cursor.lastrowid

        return jsonify({
            "message": "Post created successfully",
            "post_id": new_post_id,
            "user_id": user_id,
            "created_at": current_time.isoformat()
        }), 201

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    finally:
        # 5. Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```