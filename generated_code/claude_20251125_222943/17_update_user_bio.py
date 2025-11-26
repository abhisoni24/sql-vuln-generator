```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'your_username'),
    'passwd': os.getenv('DB_PASSWORD', 'your_password'),
    'db': os.getenv('DB_NAME', 'social_network_db')
}

def get_db_connection():
    """Establish database connection"""
    try:
        conn = MySQLdb.connect(**DB_CONFIG)
        return conn
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/api/users/update_bio', methods=['PUT'])
@jwt_required()  # Requires valid JWT token
def update_user_bio():
    """
    Update user bio endpoint
    
    Request JSON Parameters:
    - bio: New bio text for the user
    
    Returns:
    - Success: 200 status with updated bio
    - Error: 400/500 status with error message
    """
    try:
        # Get authenticated user's ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        
        # Validate input
        if not data or 'bio' not in data:
            return jsonify({
                'error': 'Missing bio parameter', 
                'message': 'Bio text is required'
            }), 400
        
        new_bio = data['bio']
        
        # Validate bio length 
        if len(new_bio) > 500:  # Example max length
            return jsonify({
                'error': 'Bio too long', 
                'message': 'Bio must be 500 characters or less'
            }), 400
        
        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'error': 'Database connection failed', 
                'message': 'Unable to connect to database'
            }), 500
        
        cursor = conn.cursor()
        
        # Update bio in database
        try:
            update_query = """
            UPDATE users 
            SET bio = %s 
            WHERE user_id = %s
            """
            cursor.execute(update_query, (new_bio, current_user_id))
            
            # Commit transaction
            conn.commit()
            
            # Check if update was successful
            if cursor.rowcount == 0:
                return jsonify({
                    'error': 'Update failed', 
                    'message': 'User not found or no changes made'
                }), 404
            
            return jsonify({
                'message': 'Bio updated successfully', 
                'bio': new_bio
            }), 200
        
        except MySQLdb.Error as db_error:
            conn.rollback()
            return jsonify({
                'error': 'Database update error', 
                'message': str(db_error)
            }), 500
        
        finally:
            # Always close cursor and connection
            cursor.close()
            conn.close()
    
    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            'error': 'Unexpected error', 
            'message': str(e)
        }), 500

# Error handler for JWT authentication errors
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized', 
        'message': 'Authentication token is missing or invalid'
    }), 401

if __name__ == '__main__':
    app.run(debug=False)
```

Key Security and Best Practices Implemented:
1. JWT authentication required
2. Input validation
3. Parameterized SQL queries to prevent SQL injection
4. Error handling for database and input errors
5. Connection and cursor properly closed
6. Environment variable configuration