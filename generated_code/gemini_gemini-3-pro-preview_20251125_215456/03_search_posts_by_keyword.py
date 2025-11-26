```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Configuration
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
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor  # Returns results as dictionaries
    )

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for posts containing a specific keyword.
    
    Query Parameters:
        q (str): The keyword to search for in post content.
        
    Returns:
        JSON: A list of matching posts or an error message.
    """
    keyword = request.args.get('q')

    # Input Validation
    if not keyword or not keyword.strip():
        return jsonify({"error": "Search keyword 'q' is required and cannot be empty."}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL Injection Prevention:
        # We use parameterized queries (%s). The database driver handles escaping.
        # We wrap the keyword in wildcards (%) for the LIKE clause.
        query = """
            SELECT 
                p.post_id, 
                p.user_id, 
                u.username,
                p.content, 
                p.created_at 
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.content LIKE %s
            ORDER BY p.created_at DESC
        """
        
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern,))
        
        posts = cursor.fetchall()

        return jsonify({
            "count": len(posts),
            "results": posts
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally, return generic error to user
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "An error occurred while accessing the database."}), 500

    except Exception as e:
        app.logger.error(f"General error: {e}")
        return jsonify({"error": "Internal server error."}), 500

    finally:
        # Resource Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```