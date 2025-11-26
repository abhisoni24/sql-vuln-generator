```python
import MySQLdb
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password',
    'db': 'your_database'
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
    return MySQLdb.connect(**db_config)

@app.route('/api/messages', methods=['POST'])
def create_message():
    """
    Endpoint to create a new message.
    Expects JSON payload: { "sender_id": int, "receiver_id": int, "content": str }
    """
    data = request.get_json()

    # 1. Input Validation
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not all([sender_id, receiver_id, content]):
        return jsonify({"error": "Missing required fields: sender_id, receiver_id, content"}), 400

    if not isinstance(sender_id, int) or not isinstance(receiver_id, int):
        return jsonify({"error": "IDs must be integers"}), 400

    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Content must be a non-empty string"}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Check if Sender and Receiver exist (Referential Integrity)
        # Note: In a production environment with Foreign Keys, the INSERT would fail automatically,
        # but checking explicitly allows for specific error messages.
        check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
        
        cursor.execute(check_user_query, (sender_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Sender with ID {sender_id} not found"}), 404

        cursor.execute(check_user_query, (receiver_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Receiver with ID {receiver_id} not found"}), 404

        # 3. Insert Message
        # Using parameterized queries (%s) to prevent SQL Injection
        insert_query = """
            INSERT INTO messages (sender_id, receiver_id, content, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (sender_id, receiver_id, content.strip()))
        
        conn.commit()
        
        new_message_id = cursor.lastrowid

        return jsonify({
            "message": "Message sent successfully",
            "data": {
                "message_id": new_message_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "timestamp": datetime.now().isoformat()
            }
        }), 201

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