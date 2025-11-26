```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
# Ideally, these should be loaded from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

"""
Database Schema Reference:
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

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """
    Searches for users by username.
    
    Query Parameters:
        username (str): The partial or full username to search for.
        
    Returns:
        JSON response containing a list of matching users or an error message.
    """
    search_query = request.args.get('username')

    # Input Validation
    if not search_query or not search_query.strip():
        return jsonify({'error': 'Username parameter is required and cannot be empty'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL Injection Prevention: Using parameterized queries (%s)
        # We select specific fields to avoid returning sensitive data if the table expands later
        sql = """
            SELECT user_id, username, email, bio, created_at 
            FROM users 
            WHERE username LIKE %s
            LIMIT 20
        """
        
        # Add wildcards for partial matching
        param = f"%{search_query}%"
        
        cursor.execute(sql, (param,))
        results = cursor.fetchall()

        return jsonify({
            'count': len(results),
            'users': results
        }), 200

    except MySQLdb.Error as e:
        # Log the specific error internally, but return a generic message to the user for security
        app.logger.error(f"Database error: {e}")
        return jsonify({'error': 'An error occurred while accessing the database'}), 500

    except Exception as e:
        app.logger.error(f"Server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=False)
```