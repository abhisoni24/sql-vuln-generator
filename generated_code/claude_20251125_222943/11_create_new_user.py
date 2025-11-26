```python
from flask import Flask, request, jsonify
import MySQLdb
import re
from datetime import datetime

app = Flask(__name__)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username', 
    'passwd': 'your_password',
    'db': 'social_network_db'
}

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_username(username):
    """Validate username format"""
    return 3 <= len(username) <= 50 and username.isalnum()

@app.route('/users/create', methods=['POST'])
def create_user():
    try:
        # Get request parameters 
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        bio = data.get('bio', '')

        # Validate input parameters
        if not username or not email:
            return jsonify({
                'error': 'Username and email are required', 
                'status': 400
            }), 400

        if not validate_username(username):
            return jsonify({
                'error': 'Invalid username format', 
                'status': 400
            }), 400

        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email format', 
                'status': 400
            }), 400

        # Establish database connection
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s", 
            (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({
                'error': 'Username or email already exists', 
                'status': 409
            }), 409

        # Insert new user
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            """INSERT INTO users 
            (username, email, bio, created_at) 
            VALUES (%s, %s, %s, %s)""", 
            (username, email, bio, current_time)
        )
        
        # Get the newly created user ID
        user_id = cursor.lastrowid

        # Commit transaction and close connection
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'message': 'User created successfully',
            'user_id': user_id,
            'status': 201
        }), 201

    except MySQLdb.Error as e:
        # Handle database errors
        return jsonify({
            'error': f'Database error: {str(e)}', 
            'status': 500
        }), 500

    except Exception as e:
        # Handle other unexpected errors
        return jsonify({
            'error': f'Unexpected error: {str(e)}', 
            'status': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```