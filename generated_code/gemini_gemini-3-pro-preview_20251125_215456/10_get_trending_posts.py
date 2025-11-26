```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables
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
    connection = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )
    return connection

@app.route('/api/posts/trending', methods=['GET'])
def get_trending_posts():
    """
    Retrieves posts from the last 7 days ordered by like count.
    
    Query Parameters:
        limit (int): Number of posts to return (default: 10, max: 50)
    """
    connection = None
    cursor = None
    try:
        # Validate and sanitize limit parameter
        limit = request.args.get('limit', default=10, type=int)
        if limit < 1:
            limit = 10
        if limit > 50:
            limit = 50

        connection = get_db_connection()
        cursor = connection.cursor()

        # SQL Query:
        # 1. Select post details and count of likes
        # 2. Join users to get author details (standard practice for post retrieval)
        # 3. Left Join likes to count them
        # 4. Filter by created_at within last 7 days
        # 5. Group by post ID
        # 6. Order by like_count descending
        query = """
            SELECT 
                p.post_id, 
                p.user_id, 
                u.username,
                p.content, 
                p.created_at, 
                COUNT(l.like_id) as like_count
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            LEFT JOIN likes l ON p.post_id = l.post_id
            WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY p.post_id, p.user_id, u.username, p.content, p.created_at
            ORDER BY like_count DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        posts = cursor.fetchall()

        return jsonify({
            "status": "success",
            "count": len(posts),
            "data": posts
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error in a real application
        return jsonify({
            "status": "error",
            "message": "Database error occurred",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "details": str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```