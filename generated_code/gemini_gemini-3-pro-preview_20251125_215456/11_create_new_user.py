```python
import MySQLdb
from flask import Flask, request, jsonify
from datetime import datetime

# Database Schema:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database_name'
}

def get_db_connection():
    return MySQLdb.connect(**DB_CONFIG)

@app.route('/users', methods=['POST'])
def create_user():
    """
    Creates a new user in the database.
    Expected JSON payload: { "username": "str", "email": "str", "bio": "str" }
    """
    data = request.get_json()

    # Input Validation
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    username = data.get('username')
    email = data.get('email')
    bio = data.get('bio', '') # Default to empty string if not provided

    if not username or not email:
        return jsonify({"error": "Missing required fields: username and email"}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parameterized query to prevent SQL Injection
        query = """
            INSERT INTO users (username, email, bio, created_at)
            VALUES (%s, %s, %s, %s)
        """
        
        current_time = datetime.now()
        cursor.execute(query, (username, email, bio, current_time))
        
        conn.commit()
        
        new_user_id = cursor.lastrowid

        return jsonify({
            "message": "User created successfully",
            "user_id": new_user_id,
            "username": username,
            "email": email
        }), 201

    except MySQLdb.IntegrityError as e:
        # Handle duplicate entries (assuming unique constraints on username or email)
        if conn:
            conn.rollback()
        return jsonify({"error": "Database integrity error (possibly duplicate username or email)", "details": str(e)}), 409

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```