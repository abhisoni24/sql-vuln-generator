```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Database Configuration (Load from environment variables in production)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

"""
Database Schema:
- users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
- posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
- followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
- messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
- notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
- user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)
"""

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/messages/recent', methods=['GET'])
def get_recent_messages():
    """
    Retrieves the most recent messages for a specific user.
    
    Query Parameters:
    - user_id (int): The ID of the user to fetch messages for (sender or receiver).
    - limit (int): The maximum number of messages to retrieve (default: 20, max: 100).
    """
    conn = None
    cursor = None
    try:
        # 1. Input Validation
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', default=20, type=int)

        if user_id is None:
            return jsonify({'error': 'Missing required parameter: user_id'}), 400
        
        if limit < 1:
            return jsonify({'error': 'Limit must be a positive integer'}), 400
        
        # Enforce a hard cap on limit to prevent performance degradation
        max_limit = 100
        if limit > max_limit:
            limit = max_limit

        # 2. Database Operation
        conn = get_db_connection()
        cursor = conn.cursor()

        # Select messages where the user is either the sender or the receiver
        # Ordered by created_at DESC to get the most recent ones
        query = """
            SELECT 
                message_id, 
                sender_id, 
                receiver_id, 
                content, 
                created_at 
            FROM messages 
            WHERE sender_id = %s OR receiver_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        
        # Execute with parameters to prevent SQL Injection
        cursor.execute(query, (user_id, user_id, limit))
        messages = cursor.fetchall()

        # 3. Data Formatting
        # Convert datetime objects to strings for JSON serialization
        results = []
        for msg in messages:
            results.append({
                'message_id': msg['message_id'],
                'sender_id': msg['sender_id'],
                'receiver_id': msg['receiver_id'],
                'content': msg['content'],
                'created_at': msg['created_at'].isoformat() if isinstance(msg['created_at'], datetime) else msg['created_at']
            })

        return jsonify({
            'status': 'success',
            'count': len(results),
            'data': results
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally
        app.logger.error(f"Database error: {e}")
        return jsonify({'error': 'An internal database error occurred'}), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
        
    finally:
        # 4. Resource Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```