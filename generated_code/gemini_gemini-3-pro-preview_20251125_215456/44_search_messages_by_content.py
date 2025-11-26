```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb.cursors import DictCursor
import os

app = Flask(__name__)

# Database Schema Reference:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

# Database configuration (Environment variables recommended for production)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/messages/search', methods=['GET'])
def search_messages():
    """
    Search messages containing a specific keyword.
    
    Query Parameters:
        - keyword (str): The text to search for within messages.
    
    Headers:
        - X-User-ID (int): The ID of the authenticated user (Simulated Auth).
    """
    keyword = request.args.get('keyword')
    # In a production environment, user_id should be extracted from a secure session or JWT token.
    # We use a header here to simulate the authenticated user context.
    current_user_id = request.headers.get('X-User-ID')

    # Input Validation
    if not keyword or not keyword.strip():
        return jsonify({'status': 'error', 'message': 'Keyword parameter is required'}), 400
    
    if not current_user_id:
        return jsonify({'status': 'error', 'message': 'Unauthorized: User ID required'}), 401

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL Query:
        # 1. Filters by keyword using LIKE operator.
        # 2. Enforces privacy: Users can only search messages they sent or received.
        # 3. Uses parameterized queries (%s) to prevent SQL Injection.
        query = """
            SELECT 
                message_id, 
                sender_id, 
                receiver_id, 
                content, 
                created_at 
            FROM messages 
            WHERE (sender_id = %s OR receiver_id = %s) 
            AND content LIKE %s
            ORDER BY created_at DESC
        """
        
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (current_user_id, current_user_id, search_pattern))
        
        results = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'count': len(results),
            'data': results
        }), 200

    except MySQLdb.Error as e:
        # Log the error internally in a real application
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```