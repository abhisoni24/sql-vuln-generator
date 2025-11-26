```python
import MySQLdb
from flask import Flask, jsonify, request

app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database_name'
}

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

@app.route('/api/users/<int:user_id>/total-likes', methods=['GET'])
def get_user_total_likes(user_id):
    """
    Calculates the total number of likes received on all posts created by a specific user.
    """
    conn = None
    cursor = None
    
    try:
        # Establish database connection
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()

        # SQL Query:
        # 1. Select from 'posts' to find content authored by the target user_id
        # 2. Join with 'likes' on post_id to find likes associated with those posts
        # 3. Count the total rows found
        query = """
            SELECT COUNT(l.like_id) 
            FROM posts p
            INNER JOIN likes l ON p.post_id = l.post_id
            WHERE p.user_id = %s
        """

        # Execute query using parameters to prevent SQL Injection
        cursor.execute(query, (user_id,))
        
        # Fetch result
        result = cursor.fetchone()
        total_likes = result[0] if result else 0

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'total_likes_received': total_likes
        }), 200

    except MySQLdb.Error as e:
        # Handle specific database errors
        return jsonify({
            'status': 'error',
            'message': 'Database operation failed',
            'details': str(e)
        }), 500

    except Exception as e:
        # Handle general server errors
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'details': str(e)
        }), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```