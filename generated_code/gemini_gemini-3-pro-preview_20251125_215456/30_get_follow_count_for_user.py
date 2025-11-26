```python
import os
import MySQLdb
from flask import Flask, jsonify

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

# Database configuration (Use environment variables in production)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME
    )

@app.route('/users/<int:user_id>/followers/count', methods=['GET'])
def get_follower_count(user_id):
    """
    Retrieves the total number of followers for a specific user.
    
    Args:
        user_id (int): The ID of the user to count followers for.
        
    Returns:
        JSON response containing the user_id and follower_count.
    """
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Parameterized query to prevent SQL injection
        # We count rows in the 'followers' table where 'followed_id' matches the requested user_id
        query = "SELECT COUNT(*) FROM followers WHERE followed_id = %s"
        cursor.execute(query, (user_id,))
        
        result = cursor.fetchone()
        count = result[0] if result else 0

        return jsonify({
            "status": "success",
            "data": {
                "user_id": user_id,
                "follower_count": count
            }
        }), 200

    except MySQLdb.Error as e:
        # Log the error in a real application
        return jsonify({
            "status": "error",
            "message": "Database error occurred",
            "details": str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred",
            "details": str(e)
        }), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == '__main__':
    app.run(debug=True)
```