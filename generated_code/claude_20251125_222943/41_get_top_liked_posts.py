```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
CORS(app)

# Rate limiting configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)

def get_db_connection():
    """Establish secure database connection"""
    try:
        connection = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            passwd=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', 'social_network'),
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

@app.route('/api/posts/top-liked', methods=['GET'])
@limiter.limit("50 per hour")
def get_top_liked_posts():
    """
    Retrieve posts with highest like counts
    Query Parameters:
    - limit: Number of top posts to retrieve (default 10, max 50)
    """
    try:
        # Validate and sanitize limit parameter
        limit = request.args.get('limit', default=10, type=int)
        limit = min(max(limit, 1), 50)  # Constrain between 1-50

        # Establish database connection
        connection = get_db_connection()
        if not connection:
            return jsonify({
                "error": "Database connection failed", 
                "status": 500
            }), 500

        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Secure query to fetch top liked posts with user details
        query = """
        SELECT 
            p.post_id, 
            p.content, 
            u.username, 
            COUNT(l.like_id) as like_count,
            p.created_at
        FROM 
            posts p
        JOIN 
            users u ON p.user_id = u.user_id
        LEFT JOIN 
            likes l ON p.post_id = l.post_id
        GROUP BY 
            p.post_id
        ORDER BY 
            like_count DESC
        LIMIT %s
        """

        cursor.execute(query, (limit,))
        top_posts = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "posts": top_posts,
            "count": len(top_posts)
        }), 200

    except Error as db_error:
        app.logger.error(f"Database query error: {db_error}")
        return jsonify({
            "error": "Internal server error", 
            "status": 500
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Unexpected error occurred", 
            "status": 500
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
```