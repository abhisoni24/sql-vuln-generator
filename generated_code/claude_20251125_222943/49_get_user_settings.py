```python
from flask import Flask, request, jsonify
import MySQLdb
from flask_cors import CORS
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

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

def validate_user_id(func):
    """Decorator to validate user_id parameter"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get('user_id')
        if not user_id or not user_id.isdigit():
            return jsonify({
                "error": "Invalid user ID",
                "status": 400
            }), 400
        return func(*args, **kwargs)
    return wrapper

@app.route('/api/user/settings', methods=['GET'])
@validate_user_id
def get_user_settings():
    """Retrieve user settings endpoint"""
    user_id = request.args.get('user_id')
    connection = get_db_connection()

    if not connection:
        return jsonify({
            "error": "Database connection failed",
            "status": 500
        }), 500

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch user settings with parameterized query
        query = """
        SELECT setting_name, setting_value 
        FROM user_settings 
        WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        
        settings = cursor.fetchall()
        
        if not settings:
            return jsonify({
                "message": "No settings found for user",
                "status": 404
            }), 404

        cursor.close()
        connection.close()

        return jsonify({
            "settings": settings,
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
            connection.close()

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Resource not found",
        "status": 404
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False), 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 5000)))
```