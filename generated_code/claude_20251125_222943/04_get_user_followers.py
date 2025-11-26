```python
from flask import Flask, jsonify, request
import MySQLdb
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

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
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

@app.route('/api/users/<int:user_id>/followers', methods=['GET'])
@limiter.limit("30 per minute")
def get_user_followers(user_id):
    """
    Retrieve all followers for a given user
    
    Args:
        user_id (int): Unique identifier for the user
    
    Returns:
        JSON response with follower details or error message
    """
    if not user_id:
        return jsonify({
            "error": "Invalid user ID",
            "status": 400
        }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "error": "Database connection failed",
            "status": 500
        }), 500

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Validate user exists first
        cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({
                "error": "User not found",
                "status": 404
            }), 404

        # Retrieve followers with user details
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.username, 
                u.email, 
                u.bio, 
                f.created_at as followed_at
            FROM followers f
            JOIN users u ON f.follower_id = u.user_id
            WHERE f.followed_id = %s
            ORDER BY f.created_at DESC
        """, (user_id,))
        
        followers = cursor.fetchall()

        return jsonify({
            "followers": followers,
            "total_followers": len(followers),
            "status": 200
        }), 200

    except MySQLdb.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({
            "error": "Internal server error",
            "status": 500
        }), 500

    finally:
        if connection:
            cursor.close()
            connection.close()

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limiting errors"""
    return jsonify({
        "error": "Too many requests",
        "description": "Rate limit exceeded",
        "status": 429
    }), 429

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False), host='0.0.0.0')
```