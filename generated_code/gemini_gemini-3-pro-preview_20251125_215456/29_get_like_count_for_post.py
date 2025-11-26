```python
from flask import Flask, jsonify, abort
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database'

# Database Schema:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

def get_db_connection():
    """Establishes a database connection."""
    try:
        connection = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            passwd=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            cursorclass=DictCursor
        )
        return connection
    except MySQLdb.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/posts/<int:post_id>/likes/count', methods=['GET'])
def count_post_likes(post_id):
    """
    Retrieves the total number of likes for a specific post.
    
    Args:
        post_id (int): The ID of the post to count likes for.
        
    Returns:
        JSON response containing the post_id and like_count.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor()
        
        # Secure parameterized query to prevent SQL injection
        query = "SELECT COUNT(*) as total_likes FROM likes WHERE post_id = %s"
        cursor.execute(query, (post_id,))
        
        result = cursor.fetchone()
        like_count = result['total_likes'] if result else 0
        
        return jsonify({
            "post_id": post_id,
            "like_count": like_count
        }), 200

    except MySQLdb.Error as e:
        return jsonify({"error": "An error occurred while fetching data", "details": str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```