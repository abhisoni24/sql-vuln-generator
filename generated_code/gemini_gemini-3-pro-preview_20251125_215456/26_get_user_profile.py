```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASS = 'your_password'
DB_NAME = 'your_dbname'

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
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    Retrieves user profile information based on user_id.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parameterized query to prevent SQL injection
        query = """
            SELECT user_id, username, email, bio, created_at 
            FROM users 
            WHERE user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        if user:
            # Convert datetime objects to strings for JSON serialization
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
            
            return jsonify({
                "status": "success",
                "data": user
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

    except MySQLdb.Error as e:
        # Log the error in a real application
        return jsonify({
            "status": "error",
            "message": "Database error occurred"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```