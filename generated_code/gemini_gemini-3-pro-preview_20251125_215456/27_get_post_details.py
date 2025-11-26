```python
from flask import Flask, jsonify, abort
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database_name'
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
    return MySQLdb.connect(**DB_CONFIG)

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_details(post_id):
    """
    Retrieves detailed information for a specific post, including author details,
    interaction counts (likes/comments), and a list of comments.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        # Use DictCursor to get results as dictionaries
        cursor = conn.cursor(DictCursor)

        # 1. Fetch Post Details, Author Info, and Interaction Counts
        # Using subqueries for counts to optimize into a single fetch for the main object
        post_query = """
            SELECT 
                p.post_id, 
                p.content, 
                p.created_at,
                u.user_id, 
                u.username,
                (SELECT COUNT(*) FROM likes WHERE post_id = %s) as like_count,
                (SELECT COUNT(*) FROM comments WHERE post_id = %s) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.post_id = %s
        """
        
        # Parameterized query to prevent SQL Injection
        cursor.execute(post_query, (post_id, post_id, post_id))
        post = cursor.fetchone()

        if not post:
            return jsonify({'error': 'Post not found'}), 404

        # 2. Fetch Comments associated with the post
        comments_query = """
            SELECT 
                c.comment_id, 
                c.content, 
                c.created_at, 
                u.user_id, 
                u.username
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """
        cursor.execute(comments_query, (post_id,))
        comments = cursor.fetchall()

        # 3. Construct the response object
        response_data = {
            'post_id': post['post_id'],
            'content': post['content'],
            'created_at': post['created_at'],
            'author': {
                'user_id': post['user_id'],
                'username': post['username']
            },
            'stats': {
                'likes': post['like_count'],
                'comments': post['comment_count']
            },
            'comments': list(comments) # Convert tuple of dicts to list
        }

        return jsonify(response_data), 200

    except MySQLdb.Error as e:
        # Log the specific database error in a real application
        return jsonify({'error': 'Database operation failed', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```