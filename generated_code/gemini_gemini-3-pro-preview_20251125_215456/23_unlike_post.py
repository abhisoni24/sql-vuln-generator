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
    'database': 'your_database'
}

# Database Schema Reference:
# users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

@app.route('/likes', methods=['DELETE'])
def remove_like():
    """
    Removes a like record based on user_id and post_id.
    Expected JSON payload: { "user_id": int, "post_id": int }
    """
    conn = None
    cursor = None
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        # Input validation
        if not user_id or not post_id:
            return jsonify({"error": "Missing required parameters: user_id and post_id"}), 400

        if not isinstance(user_id, int) or not isinstance(post_id, int):
            return jsonify({"error": "Parameters user_id and post_id must be integers"}), 400

        # Establish database connection
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to delete the like
        # Using parameterized query to prevent SQL injection
        query = "DELETE FROM likes WHERE user_id = %s AND post_id = %s"
        cursor.execute(query, (user_id, post_id))
        
        # Check if any row was actually deleted
        if cursor.rowcount == 0:
            # No record found to delete
            return jsonify({"message": "Like not found or already removed"}), 404

        # Commit the transaction
        conn.commit()

        return jsonify({"message": "Like removed successfully"}), 200

    except Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```