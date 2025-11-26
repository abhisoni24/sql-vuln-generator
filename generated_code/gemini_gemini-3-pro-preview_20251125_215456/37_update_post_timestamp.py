```python
import MySQLdb
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Database Configuration
# Ensure you update these credentials for your specific environment
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
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME
    )

@app.route('/posts/<int:post_id>/timestamp', methods=['PUT'])
def update_post_timestamp(post_id):
    """
    Updates the created_at timestamp for a specific post.
    
    Parameters:
        post_id (int): The ID of the post to update (URL parameter).
        new_timestamp (str): The new datetime string in JSON body (Format: YYYY-MM-DD HH:MM:SS).
    """
    # 1. Input Validation
    data = request.get_json()
    if not data or 'new_timestamp' not in data:
        return jsonify({'error': 'Missing new_timestamp parameter in request body'}), 400

    new_timestamp_str = data['new_timestamp']

    # Validate datetime format
    try:
        # enforcing format YYYY-MM-DD HH:MM:SS
        valid_timestamp = datetime.strptime(new_timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Expected YYYY-MM-DD HH:MM:SS'}), 400

    conn = None
    cursor = None

    try:
        # 2. Database Connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Secure Database Operation (Parameterized Query)
        # Using parameterized queries (%s) prevents SQL Injection
        sql = "UPDATE posts SET created_at = %s WHERE post_id = %s"
        cursor.execute(sql, (valid_timestamp, post_id))
        
        conn.commit()

        # Check if any row was actually updated
        if cursor.rowcount == 0:
            # Check if post exists to distinguish between "no change needed" and "post not found"
            cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (post_id,))
            if cursor.fetchone() is None:
                return jsonify({'error': 'Post not found'}), 404
            else:
                return jsonify({'message': 'Timestamp updated (No change in value detected)'}), 200

        return jsonify({
            'message': 'Post timestamp updated successfully',
            'post_id': post_id,
            'new_created_at': new_timestamp_str
        }), 200

    except MySQLdb.Error as e:
        # Log the error internally in a real app
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

    finally:
        # 4. Resource Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```