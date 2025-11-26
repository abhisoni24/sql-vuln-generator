```python
import MySQLdb
from flask import Flask, request, jsonify
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database Configuration
db_config = {
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

def get_db_connection():
    """Establishes a database connection."""
    try:
        conn = MySQLdb.connect(**db_config)
        return conn
    except MySQLdb.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/change_username', methods=['POST'])
def change_username():
    """
    Endpoint to change a user's username.
    Expects JSON payload: { "user_id": int, "new_username": str }
    """
    data = request.get_json()

    # 1. Input Validation
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    user_id = data.get('user_id')
    new_username = data.get('new_username')

    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "Invalid or missing user_id"}), 400
    
    if not new_username or not isinstance(new_username, str):
        return jsonify({"error": "Invalid or missing new_username"}), 400
    
    # Basic sanitization/validation for username length/chars could go here
    new_username = new_username.strip()
    if len(new_username) < 3:
        return jsonify({"error": "Username must be at least 3 characters long"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(DictCursor)

        # 2. Check if user exists
        # Using parameterized query to prevent SQL Injection
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        # 3. Check if new username is already taken
        check_username_query = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(check_username_query, (new_username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # If the username exists and belongs to a different user
            if existing_user['user_id'] != user_id:
                return jsonify({"error": "Username already taken"}), 409
            else:
                return jsonify({"message": "New username is the same as the current one"}), 200

        # 4. Update the username
        update_query = "UPDATE users SET username = %s WHERE user_id = %s"
        cursor.execute(update_query, (new_username, user_id))
        
        # Commit the transaction
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Username updated successfully",
            "user_id": user_id,
            "new_username": new_username
        }), 200

    except MySQLdb.Error as e:
        # Rollback in case of error to maintain data integrity
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
        
    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```