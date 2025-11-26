```python
from flask import Flask, request, jsonify
import MySQLdb
from datetime import datetime
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

# Database connection configuration
def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username',
            passwd='your_password', 
            db='social_media_db',
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

@app.route('/api/posts/date-range', methods=['GET'])
def get_posts_by_date_range():
    """
    Retrieve posts created within a specific date range
    
    Query Parameters:
    - start_date: Start date for post retrieval (YYYY-MM-DD)
    - end_date: End date for post retrieval (YYYY-MM-DD)
    - limit: Optional limit for number of posts (default 100)
    - offset: Optional offset for pagination (default 0)
    """
    try:
        # Validate and parse input parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        # Establish database connection
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'error': 'Database connection failed'
            }), 500

        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Prepared SQL query with parameterized input
        query = """
        SELECT 
            p.post_id, 
            p.content, 
            p.created_at, 
            u.username,
            (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.post_id) as like_count,
            (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id) as comment_count
        FROM 
            posts p
        JOIN 
            users u ON p.user_id = u.user_id
        WHERE 
            p.created_at BETWEEN %s AND %s
        ORDER BY 
            p.created_at DESC
        LIMIT %s OFFSET %s
        """

        # Execute query with parameters
        cursor.execute(query, (start_date, end_date, limit, offset))
        posts = cursor.fetchall()

        # Close database connections
        cursor.close()
        connection.close()

        # Return results
        return jsonify({
            'posts': posts,
            'count': len(posts)
        }), 200

    except MySQLdb.Error as db_error:
        app.logger.error(f"Database query error: {db_error}")
        return jsonify({
            'error': 'Database query failed'
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred'
        }), 500

# Rate limiting configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```