```python
from flask import Flask, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='your_username', 
            passwd='your_password',
            db='social_network_db',
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        raise

@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_user_messages():
    try:
        # Validate user authentication 
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        
        # Validate input
        if not user_id:
            raise BadRequest("User ID is required")
        
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to retrieve messages where user is sender or receiver
        query = """
        SELECT 
            message_id, 
            sender_id, 
            receiver_id, 
            content, 
            created_at 
        FROM messages 
        WHERE 
            (sender_id = %s OR receiver_id = %s)
            AND (sender_id = %s OR receiver_id = %s)
        ORDER BY created_at DESC
        """
        
        # Execute query with parameters
        cursor.execute(query, (current_user_id, current_user_id, user_id, user_id))
        
        # Fetch all matching messages
        messages = cursor.fetchall()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        # Return messages as JSON response
        return jsonify({
            'status': 'success',
            'messages': messages
        }), 200
    
    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except MySQLdb.Error as e:
        return jsonify({
            'status': 'error', 
            'message': f'Database error: {str(e)}'
        }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```