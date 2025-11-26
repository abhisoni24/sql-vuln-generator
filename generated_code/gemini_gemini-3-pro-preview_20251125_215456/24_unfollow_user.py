```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error

app = Flask(__name__)

# Database Configuration
# Ensure you update these credentials for your specific environment
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'

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
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

@app.route('/api/unfollow', methods=['DELETE'])
def remove_follow():
    """
    Removes a follow relationship between two users.
    
    Expected JSON Payload:
    {
        "follower_id": int,
        "followed_id": int
    }
    """
    data = request.get_json()

    # 1. Input Validation
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')

    if not isinstance(follower_id, int) or not isinstance(followed_id, int):
        return jsonify({"error": "Invalid parameters. 'follower_id' and 'followed_id' must be integers."}), 400

    if follower_id == followed_id:
        return jsonify({"error": "Users cannot unfollow themselves."}), 400

    conn = None
    cursor = None

    try:
        # 2. Database Connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Execute Deletion
        # Using parameterized queries (%s) to prevent SQL Injection
        query = "DELETE FROM followers WHERE follower_id = %s AND followed_id = %s"
        cursor.execute(query, (follower_id, followed_id))
        
        # 4. Check if any row was actually deleted
        if cursor.rowcount == 0:
            # No relationship found to delete
            return jsonify({"message": "Relationship does not exist or already removed."}), 404

        # 5. Commit Transaction
        conn.commit()

        return jsonify({"message": "Successfully unfollowed user."}), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

    finally:
        # 6. Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```