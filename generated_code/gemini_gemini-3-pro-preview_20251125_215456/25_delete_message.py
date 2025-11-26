```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error

app = Flask(__name__)

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = 'password'
DB_NAME = 'social_media_db'

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
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """
    Deletes a message based on message_id.
    Security: Checks if the requester is the sender of the message to prevent IDOR.
    """
    # In a real production environment, current_user_id should be extracted 
    # from a secure session or JWT token (e.g., g.user.id).
    # For this runnable snippet, we accept it from the JSON body or query params.
    current_user_id = request.args.get('current_user_id') or request.json.get('current_user_id')

    if not current_user_id:
        return jsonify({"error": "Authentication required (missing current_user_id)"}), 401

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Secure: Use parameterized queries to prevent SQL Injection.
        # Secure: Include 'sender_id' in the WHERE clause to ensure users 
        # can only delete their own messages (Authorization).
        query = "DELETE FROM messages WHERE message_id = %s AND sender_id = %s"
        
        # Execute the query
        cursor.execute(query, (message_id, current_user_id))
        conn.commit()

        # Check if any row was actually affected
        if cursor.rowcount == 0:
            # If no rows deleted, either message doesn't exist or user doesn't own it
            return jsonify({
                "error": "Message not found or you do not have permission to delete it."
            }), 404

        return jsonify({"message": "Message deleted successfully", "id": message_id}), 200

    except Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```