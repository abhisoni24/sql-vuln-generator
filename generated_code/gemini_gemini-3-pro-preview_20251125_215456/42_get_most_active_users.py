```python
import MySQLdb
from flask import Flask, request, jsonify
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'db_user'
app.config['MYSQL_PASSWORD'] = 'db_password'
app.config['MYSQL_DB'] = 'social_media_db'

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
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=DictCursor
    )

@app.route('/api/users/most-posts', methods=['GET'])
def get_users_with_most_posts():
    """
    Retrieves users with the highest number of posts.
    
    Query Parameters:
        limit (int): The maximum number of users to return (default: 10).
    """
    connection = None
    cursor = None
    
    try:
        # 1. Validate Input
        limit_param = request.args.get('limit', default=10)
        
        try:
            limit = int(limit_param)
            if limit < 1:
                return jsonify({"error": "Limit must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "Limit must be an integer"}), 400

        # 2. Connect to Database
        connection = get_db_connection()
        cursor = connection.cursor()

        # 3. Execute Query
        # Using parameterized query to prevent SQL Injection
        query = """
            SELECT 
                u.user_id, 
                u.username, 
                u.email, 
                COUNT(p.post_id) as post_count
            FROM users u
            JOIN posts p ON u.user_id = p.user_id
            GROUP BY u.user_id
            ORDER BY post_count DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()

        # 4. Return Response
        return jsonify({
            "status": "success",
            "count": len(results),
            "data": results
        }), 200

    except MySQLdb.Error as e:
        # Handle Database specific errors
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    
    except Exception as e:
        # Handle general server errors
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
    finally:
        # 5. Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```