```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error
import re

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'

# Database Schema:
# users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME
    )

def is_valid_email(email):
    """Basic regex validation for email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

@app.route('/api/users/<int:user_id>/email', methods=['PUT'])
def update_user_email(user_id):
    """
    Updates a user's email address.
    
    Parameters:
        user_id (int): The ID of the user to update (from URL).
        email (str): The new email address (from JSON body).
    """
    
    # SECURITY NOTE: In a production environment, you must implement authentication 
    # and authorization checks here (e.g., JWT or Session) to ensure the requester 
    # is allowed to modify this specific user_id (IDOR protection).

    # 1. Validate Request Content Type
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    new_email = data.get('email')

    # 2. Validate Input Parameters
    if not new_email:
        return jsonify({"error": "New email is required"}), 400

    if not is_valid_email(new_email):
        return jsonify({"error": "Invalid email format"}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Check if user exists
        check_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_query, (user_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "User not found"}), 404

        # 4. Update the email
        # Using parameterized queries to prevent SQL Injection
        update_query = "UPDATE users SET email = %s WHERE user_id = %s"
        cursor.execute(update_query, (new_email, user_id))
        
        conn.commit()

        return jsonify({
            "message": "Email updated successfully",
            "user_id": user_id,
            "new_email": new_email
        }), 200

    except MySQLdb.IntegrityError as e:
        # Handle potential unique constraint violations (if email must be unique)
        if conn:
            conn.rollback()
        return jsonify({"error": "Email already in use or database integrity error", "details": str(e)}), 409

    except Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        # 5. Clean up resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```