```python
from flask import Flask, jsonify, request, abort
import MySQLdb
from MySQLdb import IntegrityError

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'

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
    """Establishes a connection to the MySQL database."""
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes a user from the database.
    
    Note: This endpoint assumes the database schema is configured with 
    ON DELETE CASCADE for foreign keys in related tables (posts, comments, etc.).
    If not, manual deletion of related records within the transaction is required.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Start transaction
        conn.begin()

        # Check if user exists first
        check_query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_query, (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.rollback()
            return jsonify({"error": "User not found"}), 404

        # Delete the user
        # Using parameterized query to prevent SQL Injection
        delete_query = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))

        # Commit the transaction
        conn.commit()

        return jsonify({
            "message": "User and associated data deleted successfully",
            "user_id": user_id
        }), 200

    except IntegrityError as e:
        if conn:
            conn.rollback()
        # This catches foreign key constraint failures if ON DELETE CASCADE is missing
        return jsonify({"error": "Database integrity error. Cannot delete user due to existing dependencies.", "details": str(e)}), 409

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

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