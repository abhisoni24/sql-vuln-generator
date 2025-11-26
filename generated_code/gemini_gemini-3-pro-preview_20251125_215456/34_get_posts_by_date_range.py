```python
import MySQLdb
from MySQLdb.cursors import DictCursor
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASS = 'your_password'
DB_NAME = 'social_media_db'

"""
Database Schema Reference:
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
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME,
        cursorclass=DictCursor
    )

@app.route('/api/posts/date-range', methods=['GET'])
def get_posts_by_date_range():
    """
    Retrieve posts created within a specific date range.
    
    Query Parameters:
    - start_date: Format YYYY-MM-DD (Required)
    - end_date: Format YYYY-MM-DD (Required)
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # 1. Input Validation
    if not start_date_str or not end_date_str:
        return jsonify({
            "error": "Missing parameters", 
            "message": "Both 'start_date' and 'end_date' are required."
        }), 400

    try:
        # Validate date format
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Adjust end_date to include the full day (23:59:59)
        end_date = end_date.replace(hour=23, minute=59, second=59)

    except ValueError:
        return jsonify({
            "error": "Invalid date format", 
            "message": "Dates must be in YYYY-MM-DD format."
        }), 400

    if start_date > end_date:
        return jsonify({
            "error": "Invalid range", 
            "message": "start_date cannot be after end_date."
        }), 400

    conn = None
    cursor = None

    try:
        # 2. Database Operation
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query using parameterized inputs to prevent SQL injection
        query = """
            SELECT post_id, user_id, content, created_at 
            FROM posts 
            WHERE created_at BETWEEN %s AND %s
            ORDER BY created_at DESC
        """
        
        cursor.execute(query, (start_date, end_date))
        posts = cursor.fetchall()

        # 3. Response Formatting
        results = []
        for post in posts:
            results.append({
                "post_id": post['post_id'],
                "user_id": post['user_id'],
                "content": post['content'],
                # Convert datetime object to string for JSON serialization
                "created_at": post['created_at'].isoformat() if post['created_at'] else None
            })

        return jsonify({
            "status": "success",
            "count": len(results),
            "data": results
        }), 200

    except MySQLdb.Error as e:
        # Log the specific database error internally here
        return jsonify({
            "error": "Database error", 
            "message": "An error occurred while retrieving posts."
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Internal server error", 
            "message": str(e)
        }), 500

    finally:
        # 4. Resource Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```