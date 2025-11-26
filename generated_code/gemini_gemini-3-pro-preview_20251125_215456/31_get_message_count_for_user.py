```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database'

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
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )

@app.route('/api/users/<int:user_id>/messages/count', methods=['GET'])
def get_user_message_count(user_id):
    """
    Retrieves the total count of messages for a specific user.
    Counts messages where the user is either the sender or the receiver.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists first (Optional but recommended for 404s)
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404

        # Query to count messages where user is sender OR receiver
        # Using parameterized queries to prevent SQL injection
        query = """
            SELECT COUNT(*) 
            FROM messages 
            WHERE sender_id = %s OR receiver_id = %s
        """
        cursor.execute(query, (user_id, user_id))
        
        result = cursor.fetchone()
        # MySQLdb returns a tuple, index 0 is the count
        total_messages = result[0] if result else 0

        return jsonify({
            'user_id': user_id,
            'total_messages': total_messages
        }), 200

    except MySQLdb.Error as e:
        # Log the error in a real application
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```