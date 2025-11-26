```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
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
        raise InternalServerError("Database connection failed")

@app.route('/api/messages/search', methods=['GET'])
def search_messages():
    """
    Search messages containing a specific keyword
    Query Parameters:
    - keyword: Text to search within message content
    - user_id: Optional parameter to filter messages for a specific user
    - limit: Optional parameter to limit number of results (default 50)
    """
    try:
        # Validate and extract query parameters
        keyword = request.args.get('keyword', '').strip()
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', default=50, type=int)

        # Input validation
        if not keyword:
            raise BadRequest("Keyword is required")
        
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Construct dynamic query with optional user_id filter
        query = """
        SELECT m.message_id, m.sender_id, m.receiver_id, 
               m.content, m.created_at, 
               u_sender.username as sender_username,
               u_receiver.username as receiver_username
        FROM messages m
        JOIN users u_sender ON m.sender_id = u_sender.user_id
        JOIN users u_receiver ON m.receiver_id = u_receiver.user_id
        WHERE m.content LIKE %s
        """
        params = [f"%{keyword}%"]

        # Add optional user_id filter
        if user_id:
            query += " AND (m.sender_id = %s OR m.receiver_id = %s)"
            params.extend([user_id, user_id])

        # Add limit
        query += " LIMIT %s"
        params.append(limit)

        # Execute query
        cursor.execute(query, params)
        results = cursor.fetchall()

        # Close database connections
        cursor.close()
        conn.close()

        # Return results
        return jsonify({
            'status': 'success',
            'total_results': len(results),
            'messages': results
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
            'message': 'Database query failed'
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'An unexpected error occurred'
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```