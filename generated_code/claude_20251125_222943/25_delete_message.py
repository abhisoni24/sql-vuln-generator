```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

messages_bp = Blueprint('messages', __name__)

def get_db_connection():
    """Establish database connection"""
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username', 
            passwd='your_password',
            db='social_media_db',
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        raise Exception(f"Database connection error: {str(e)}")

@messages_bp.route('/messages/delete/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """
    Delete a specific message by message_id
    Requires JWT authentication
    """
    current_user_id = get_jwt_identity()
    
    if not message_id:
        raise BadRequest("Message ID is required")
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify message belongs to current user
        cursor.execute("""
            SELECT sender_id, receiver_id 
            FROM messages 
            WHERE message_id = %s
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            return jsonify({
                "error": "Message not found",
                "status": 404
            }), 404
        
        # Check if current user is sender or receiver
        if message[0] != current_user_id and message[1] != current_user_id:
            return jsonify({
                "error": "Unauthorized to delete this message",
                "status": 403
            }), 403
        
        # Delete the message
        cursor.execute("""
            DELETE FROM messages 
            WHERE message_id = %s
        """, (message_id,))
        
        connection.commit()
        
        return jsonify({
            "message": "Message deleted successfully",
            "status": 200
        }), 200
    
    except MySQLdb.Error as e:
        if connection:
            connection.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}",
            "status": 500
        }), 500
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
```

Key Security and Functional Features:
- JWT authentication required
- Verifies message ownership before deletion
- Prevents unauthorized message deletion
- Comprehensive error handling
- Proper database connection management
- Uses parameterized queries to prevent SQL injection
- Returns appropriate HTTP status codes
- Closes database connections in finally block
- Rolls back transaction on database errors

Note: Replace 'your_username' and 'your_password' with actual database credentials.