```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database configuration
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
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/users/search', methods=['GET'])
def search_users_by_bio():
    """
    Search for users whose bio contains a specific keyword.
    Query Parameter: keyword (string)
    """
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Secure parameterized query to prevent SQL injection
        # We append the wildcards (%) to the parameter value in Python, not in the SQL string
        query = "SELECT user_id, username, email, bio, created_at FROM users WHERE bio LIKE %s"
        search_pattern = f"%{keyword}%"
        
        cursor.execute(query, (search_pattern,))
        results = cursor.fetchall()

        users = []
        for row in results:
            users.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'email': row['email'],
                'bio': row['bio'],
                'created_at': row['created_at']
            })

        return jsonify({'count': len(users), 'users': users}), 200

    except MySQLdb.Error as e:
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```