```python
from flask import Blueprint, jsonify, request
import MySQLdb
from functools import wraps
import os

likes_bp = Blueprint('likes', __name__)

# Database connection configuration
def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            passwd=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', 'social_network'),
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return None

# Error handling decorator
def handle_db_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except MySQLdb.Error as e:
            return jsonify({
                'error': 'Database error',
                'message': str(e)
            }), 500
        except ValueError as e:
            return jsonify({
                'error': 'Invalid input',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'error': 'Unexpected error',
                'message': str(e)
            }), 500
    return decorated_function

@likes_bp.route('/post/likes', methods=['GET'])
@handle_db_errors
def get_post_likes_count():
    # Validate post_id parameter
    post_id = request.args.get('post_id')
    if not post_id:
        return jsonify({
            'error': 'Missing post_id parameter'
        }), 400
    
    try:
        post_id = int(post_id)
    except ValueError:
        return jsonify({
            'error': 'Invalid post_id format'
        }), 400

    # Establish database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'error': 'Database connection failed'
        }), 500

    try:
        # Create cursor
        cursor = conn.cursor()

        # Query to count total likes for specific post
        query = """
        SELECT COUNT(*) as total_likes 
        FROM likes 
        WHERE post_id = %s
        """
        
        # Execute query
        cursor.execute(query, (post_id,))
        
        # Fetch result
        result = cursor.fetchone()
        
        # Close cursor and connection
        cursor.close()
        conn.close()

        # Return likes count
        return jsonify({
            'post_id': post_id,
            'total_likes': result[0]
        }), 200

    except MySQLdb.Error as e:
        # Close connection in case of error
        if conn:
            conn.close()
        raise
```

Key features:
- Secure database connection using environment variables
- Comprehensive error handling
- Parameterized query to prevent SQL injection
- Validates input parameters
- Uses Blueprint for modular routing
- Closes database connections properly
- Returns JSON response with status codes
- Handles potential database and input errors

Note: Requires `mysqlclient` library and proper environment configuration.