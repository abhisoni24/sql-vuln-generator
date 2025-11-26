```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database Configuration
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
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/users/search', methods=['GET'])
def search_user_by_email():
    """
    Searches for a user by email.
    
    Query Parameters:
        email (str): The email address to search for.
        
    Returns:
        JSON: User object if found, error message otherwise.
    """
    email = request.args.get('email')

    # Input Validation
    if not email:
        return jsonify({'status': 'error', 'message': 'Email parameter is required'}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Secure Parameterized Query to prevent SQL Injection
        query = """
            SELECT user_id, username, email, bio, created_at 
            FROM users 
            WHERE email = %s
        """
        
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
            return jsonify({'status': 'success', 'data': user}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'User not found'}), 404

    except MySQLdb.Error as e:
        # Log the specific error internally, return generic error to user
        print(f"Database Error: {e}")
        return jsonify({'status': 'error', 'message': 'Database operation failed'}), 500

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=False)
```