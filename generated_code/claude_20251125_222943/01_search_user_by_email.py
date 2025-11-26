```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Establish secure database connection"""
    try:
        conn = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

@app.route('/api/user/search', methods=['GET'])
def search_user_by_email():
    """
    Search user by email and return user information
    
    Query Parameters:
    - email: User's email address (required)
    
    Returns:
    - User details if found
    - 400 error if email is missing
    - 404 error if user not found
    """
    try:
        email = request.args.get('email')
        
        if not email:
            raise BadRequest("Email parameter is required")
        
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Parameterized query to prevent SQL injection
        query = """
        SELECT user_id, username, email, bio, created_at 
        FROM users 
        WHERE email = %s
        """
        
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user), 200
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    
    except MySQLdb.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```