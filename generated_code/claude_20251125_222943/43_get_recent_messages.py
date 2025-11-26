```python
from flask import Flask, request, jsonify
import MySQLdb
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

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
        return None

@app.route('/api/messages/recent', methods=['GET'])
def get_recent_messages():
    try:
        # Validate and parse input parameters
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Input validation
        if not user_id:
            return jsonify({
                'error': 'User ID is required',
                'status': 400
            }), 400
        
        if limit <= 0 or limit > 100:
            return jsonify({
                'error': 'Invalid limit. Must be between 1 and 100',
                'status': 400
            }), 400
        
        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'error': 'Database connection failed',
                'status': 500
            }), 500
        
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to fetch recent messages for the user
        query = """
        SELECT 
            m.message_id, 
            m.sender_id, 
            u.username as sender_username,
            m.receiver_id,
            m.content, 
            m.created_at
        FROM 
            messages m
        JOIN 
            users u ON m.sender_id = u.user_id
        WHERE 
            m.receiver_id = %s OR m.sender_id = %s
        ORDER BY 
            m.created_at DESC
        LIMIT %s
        """
        
        cursor.execute(query, (user_id, user_id, limit))
        messages = cursor.fetchall()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        return jsonify({
            'messages': messages,
            'count': len(messages),
            'status': 200
        }), 200
    
    except MySQLdb.Error as db_error:
        app.logger.error(f"Database query error: {db_error}")
        return jsonify({
            'error': 'Database query failed',
            'status': 500
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```