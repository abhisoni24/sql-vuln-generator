```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
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

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        passwd=DB_CONFIG['passwd'],
        db=DB_CONFIG['db'],
        cursorclass=DictCursor
    )

@app.route('/api/users/<int:user_id>/settings', methods=['GET'])
def get_user_settings(user_id):
    """
    Retrieves settings for a specific user.
    
    Args:
        user_id (int): The ID of the user to retrieve settings for.
        
    Returns:
        JSON response containing user settings or error message.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists first
        user_check_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(user_check_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404

        # Retrieve user settings using parameterized query to prevent SQL Injection
        query = "SELECT setting_name, setting_value FROM user_settings WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        
        rows = cursor.fetchall()
        
        # Convert list of rows into a key-value dictionary
        settings = {row['setting_name']: row['setting_value'] for row in rows}

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'settings': settings
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally
        print(f"Database Error: {e}")
        return jsonify({'error': 'Database operation failed'}), 500
        
    except Exception as e:
        # Log general errors
        print(f"Server Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
        
    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```