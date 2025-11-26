```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import IntegrityError
import datetime

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables for credentials
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASS = 'your_password'
DB_NAME = 'social_media_db'

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
        passwd=DB_PASS,
        db=DB_NAME
    )

@app.route('/like', methods=['POST'])
def create_like():
    """
    Creates a like record for a specific post by a specific user.
    Expected JSON payload: { "user_id": int, "post_id": int }
    """
    data = request.get_json()

    # Input Validation
    if not data or 'user_id' not in data or 'post_id' not in data:
        return jsonify({'error': 'Missing user_id or post_id parameter'}), 400

    user_id = data['user_id']
    post_id = data['post_id']

    # Type validation
    if not isinstance(user_id, int) or not isinstance(post_id, int):
        return jsonify({'error': 'user_id and post_id must be integers'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the like already exists to prevent duplicates
        # (Assuming application logic requires unique likes per user/post pair)
        check_query = "SELECT like_id FROM likes WHERE user_id = %s AND post_id = %s"
        cursor.execute(check_query, (user_id, post_id))
        existing_like = cursor.fetchone()

        if existing_like:
            return jsonify({'message': 'User has already liked this post'}), 409 # Conflict

        # Insert the new like record
        # Using NOW() for created_at to let the database handle the timestamp
        insert_query = "INSERT INTO likes (user_id, post_id, created_at) VALUES (%s, %s, NOW())"
        cursor.execute(insert_query, (user_id, post_id))
        
        conn.commit()

        return jsonify({
            'message': 'Like created successfully',
            'user_id': user_id,
            'post_id': post_id
        }), 201

    except IntegrityError as e:
        # This catches Foreign Key constraints (if user or post doesn't exist)
        # or Unique constraints (if the DB schema enforces unique user_id+post_id)
        if conn:
            conn.rollback()
        
        error_code = e.args[0]
        # MySQL error code 1452: Cannot add or update a child row: a foreign key constraint fails
        if error_code == 1452:
            return jsonify({'error': 'Invalid user_id or post_id. Resource does not exist.'}), 404
        # MySQL error code 1062: Duplicate entry
        elif error_code == 1062:
            return jsonify({'error': 'Like already exists.'}), 409
        else:
            return jsonify({'error': 'Database integrity error', 'details': str(e)}), 500

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```