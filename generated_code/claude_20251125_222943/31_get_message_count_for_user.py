```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

@app.route('/api/messages/count', methods=['GET'])
@limiter.limit("10 per minute")
def count_user_messages():
    """
    Endpoint to count total messages for a specific user
    
    Query Parameters:
    - user_id: Integer representing the user's unique identifier
    
    Returns:
    - JSON response with total message count or error details
    """
    try:
        # Validate input parameters
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                "status": "error", 
                "message": "Invalid or missing user_id"
            }), 400
        
        # Establish database connection
        db = get_db_connection()
        if not db:
            return jsonify({
                "status": "error", 
                "message": "Database connection failed"
            }), 500
        
        cursor = db.cursor()
        
        # Count total messages (sent and received)
        query = """
        SELECT 
            COUNT(*) as total_messages 
        FROM 
            messages 
        WHERE 
            sender_id = %s OR receiver_id = %s
        """
        
        cursor.execute(query, (user_id, user_id))
        result = cursor.fetchone()
        
        # Close database resources
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "total_messages": result[0] if result else 0
        }), 200
    
    except MySQLdb.Error as db_error:
        app.logger.error(f"Database query error: {db_error}")
        return jsonify({
            "status": "error", 
            "message": "Database query failed"
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Internal server error"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Resource not found"}), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({"status": "error", "message": "Too many requests"}), 429

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
```