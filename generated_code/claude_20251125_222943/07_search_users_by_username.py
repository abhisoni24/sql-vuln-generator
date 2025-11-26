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
        raise

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """
    Search users by username with optional filtering
    Query Parameters:
    - username: Partial or full username to search
    - limit: Maximum number of results (default 10)
    - offset: Pagination offset (default 0)
    """
    try:
        # Validate and sanitize input parameters
        username = request.args.get('username', '').strip()
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))

        # Validate input
        if not username:
            raise BadRequest("Username parameter is required")
        
        if limit > 100:
            limit = 100  # Prevent excessive data retrieval

        # Establish database connection
        connection = get_db_connection()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Parameterized query to prevent SQL injection
        query = """
        SELECT user_id, username, email, bio, created_at 
        FROM users 
        WHERE username LIKE %s 
        LIMIT %s OFFSET %s
        """
        search_param = f"%{username}%"
        
        cursor.execute(query, (search_param, limit, offset))
        results = cursor.fetchall()

        # Close database resources
        cursor.close()
        connection.close()

        # Return results
        return jsonify({
            'status': 'success',
            'users': results,
            'count': len(results)
        }), 200

    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except MySQLdb.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Database error occurred'
        }), 500
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid input parameters'
        }), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False), 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 5000)))
```