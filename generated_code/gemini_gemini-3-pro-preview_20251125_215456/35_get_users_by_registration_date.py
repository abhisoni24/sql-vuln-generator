```python
from flask import Flask, request, jsonify
import MySQLdb
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database_name'
}

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

@app.route('/api/users/search-by-date', methods=['GET'])
def get_users_by_date_range():
    """
    Retrieve users registered within a specific date range.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 1. Input Validation
    if not start_date or not end_date:
        return jsonify({'error': 'Missing required parameters: start_date and end_date'}), 400

    try:
        # Validate date format
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    conn = None
    cursor = None

    try:
        # 2. Database Connection
        conn = MySQLdb.connect(**DB_CONFIG)
        # Use DictCursor to get results as dictionaries instead of tuples
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # 3. Secure SQL Execution (Parameterized Query)
        # We cast created_at to DATE to ensure we compare just the date part, ignoring time
        sql = """
            SELECT user_id, username, email, bio, created_at 
            FROM users 
            WHERE DATE(created_at) BETWEEN %s AND %s
            ORDER BY created_at DESC
        """
        
        cursor.execute(sql, (start_date, end_date))
        results = cursor.fetchall()

        # 4. Data Formatting
        users = []
        for row in results:
            users.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'email': row['email'],
                'bio': row['bio'],
                # Convert datetime object to string for JSON serialization
                'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            'status': 'success',
            'count': len(users),
            'data': users
        }), 200

    except MySQLdb.Error as e:
        # Log the specific error internally in a real app
        return jsonify({'error': 'Database operation failed', 'details': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
        
    finally:
        # 5. Resource Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```