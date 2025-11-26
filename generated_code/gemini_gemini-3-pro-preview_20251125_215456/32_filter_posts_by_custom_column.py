```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database configuration
# In a production environment, use environment variables for credentials
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

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
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/posts/filter', methods=['GET'])
def filter_posts():
    """
    Filters posts based on a specific column and value.
    
    Query Parameters:
    - column_name: The name of the column to filter by (e.g., 'user_id', 'post_id').
    - value: The value to match.
    """
    column_name = request.args.get('column_name')
    value = request.args.get('value')

    if not column_name or not value:
        return jsonify({'error': 'Missing column_name or value parameters'}), 400

    # Security: Whitelist allowed columns to prevent SQL Injection via column identifiers.
    # SQL parameters (%s) only protect values, not table/column names.
    ALLOWED_COLUMNS = {'post_id', 'user_id', 'content', 'created_at'}
    
    if column_name not in ALLOWED_COLUMNS:
        return jsonify({'error': 'Invalid or unauthorized column name'}), 400

    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construct query safely using the whitelisted column name
        # and parameterized query for the value
        query = f"SELECT post_id, user_id, content, created_at FROM posts WHERE {column_name} = %s"
        
        cursor.execute(query, (value,))
        posts = cursor.fetchall()

        return jsonify({
            'count': len(posts),
            'posts': posts
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