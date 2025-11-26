```python
from flask import Flask, request, jsonify
import MySQLdb
import re
from flask_jwt_extended import jwt_required, get_jwt_identity

app = Flask(__name__)

def get_db_connection():
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
        print(f"Database connection error: {e}")
        return None

def validate_username(username):
    """
    Validate username format
    - 3-20 characters
    - Alphanumeric and underscores only
    - Cannot start with number
    """
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username):
        return False
    return True

@app.route('/user/change_username', methods=['PUT'])
@jwt_required()  # Requires valid JWT token
def change_username():
    try:
        # Get current authenticated user's ID
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        new_username = data.get('username', '').strip()

        # Validate username
        if not new_username:
            return jsonify({
                'error': 'Username is required',
                'status': 400
            }), 400

        if not validate_username(new_username):
            return jsonify({
                'error': 'Invalid username format',
                'status': 400
            }), 400

        # Database connection
        db = get_db_connection()
        if not db:
            return jsonify({
                'error': 'Database connection failed',
                'status': 500
            }), 500

        cursor = db.cursor()

        # Check if username already exists
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (new_username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            db.close()
            return jsonify({
                'error': 'Username already taken',
                'status': 409
            }), 409

        # Update username
        cursor.execute("""
            UPDATE users 
            SET username = %s 
            WHERE user_id = %s
        """, (new_username, current_user_id))
        
        # Commit transaction
        db.commit()

        # Close database connection
        cursor.close()
        db.close()

        return jsonify({
            'message': 'Username updated successfully',
            'status': 200,
            'new_username': new_username
        }), 200

    except MySQLdb.Error as db_error:
        # Rollback in case of database error
        if 'db' in locals() and db:
            db.rollback()
            db.close()
        
        return jsonify({
            'error': f'Database error: {str(db_error)}',
            'status': 500
        }), 500

    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'status': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
```