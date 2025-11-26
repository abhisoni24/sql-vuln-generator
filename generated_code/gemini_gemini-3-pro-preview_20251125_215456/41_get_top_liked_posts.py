```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Database Configuration
# In a production environment, use environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_media_db')

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

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/posts/top', methods=['GET'])
def get_top_liked_posts():
    """
    Retrieves posts with the highest like counts.
    
    Query Parameters:
        limit (int): The maximum number of posts to return (default: 10, max: 100).
    
    Returns:
        JSON response containing the list of posts with like counts.
    """
    connection = None
    cursor = None
    
    try:
        # Input Validation
        limit_param = request.args.get('limit', default=10)
        
        try:
            limit = int(limit_param)
        except ValueError:
            return jsonify({'error': 'Invalid limit parameter. Must be an integer.'}), 400
            
        # Enforce bounds to prevent excessive load
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100

        connection = get_db_connection()
        cursor = connection.cursor()

        # SQL Query: Join posts and likes, count likes, sort descending
        # Using LEFT JOIN to ensure posts are returned even if the count logic changes,
        # though typically top posts imply > 0 likes.
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
            GROUP BY p.post_id
            ORDER BY like_count DESC
            LIMIT %s
        """
        
        # Execute query with parameterized input to prevent SQL injection
        cursor.execute(query, (limit,))
        results = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'count': len(results),
            'data': results
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally (omitted for brevity)
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
        
    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```