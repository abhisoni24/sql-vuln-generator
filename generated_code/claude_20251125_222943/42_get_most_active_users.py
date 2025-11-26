```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username',
            passwd='your_password', 
            db='social_network_db',
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

def db_error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            app.logger.error(f"Database error: {e}")
            return jsonify({
                "status": "error",
                "message": "Database operation failed",
                "error": str(e)
            }), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return jsonify({
                "status": "error", 
                "message": "An unexpected error occurred",
                "error": str(e)
            }), 500
    return decorated_function

@app.route('/users/most_posts', methods=['GET'])
@db_error_handler
def get_users_most_posts():
    """
    Retrieve users with the most posts
    Query parameters:
    - limit: Number of top users to retrieve (default 10)
    """
    # Get limit from query parameter, default to 10 if not provided
    limit = request.args.get('limit', default=10, type=int)
    
    # Validate limit is positive
    if limit <= 0:
        return jsonify({
            "status": "error",
            "message": "Limit must be a positive integer"
        }), 400

    # Establish database connection
    connection = get_db_connection()
    if not connection:
        return jsonify({
            "status": "error", 
            "message": "Unable to connect to database"
        }), 500

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to get users with most posts, ordered by post count
        query = """
        SELECT 
            u.user_id, 
            u.username, 
            u.email, 
            COUNT(p.post_id) as post_count
        FROM 
            users u
        LEFT JOIN 
            posts p ON u.user_id = p.user_id
        GROUP BY 
            u.user_id, u.username, u.email
        ORDER BY 
            post_count DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        users = cursor.fetchall()
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "data": users
        }), 200

    except Error as e:
        # Ensure connection is closed in case of error
        if connection:
            connection.close()
        raise  # Re-raise to be caught by error handler

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```