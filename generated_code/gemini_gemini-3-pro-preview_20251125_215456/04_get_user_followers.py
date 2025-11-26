```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database'

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

@app.route('/users/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    """
    Retrieves all followers for a specific user_id.
    
    Args:
        user_id (int): The ID of the user whose followers are being requested.
        
    Returns:
        JSON response containing the list of followers or error message.
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First, verify the user exists
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        # Retrieve followers
        # We join 'followers' with 'users' to get the profile details of the people following the target user.
        # follower_id = the person doing the following
        # followed_id = the target user (user_id parameter)
        query = """
            SELECT 
                u.user_id, 
                u.username, 
                u.email, 
                u.bio, 
                f.created_at as followed_at
            FROM users u
            INNER JOIN followers f ON u.user_id = f.follower_id
            WHERE f.followed_id = %s
            ORDER BY f.created_at DESC
        """
        
        # Execute query with parameterized input to prevent SQL injection
        cursor.execute(query, (user_id,))
        followers = cursor.fetchall()

        return jsonify({
            "user_id": user_id,
            "count": len(followers),
            "followers": followers
        }), 200

    except MySQLdb.Error as e:
        # Log the error in a real application
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
```