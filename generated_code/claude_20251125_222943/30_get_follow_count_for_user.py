```python
from flask import Flask, request, jsonify
import MySQLdb
from MySQLdb import Error
from functools import wraps

app = Flask(__name__)

# Database connection configuration
def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username',
            passwd='your_password', 
            db='social_network_db',
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return None

# Error handling decorator
def handle_db_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({
                'error': 'Database operation failed', 
                'message': str(e)
            }), 500
        except ValueError as ve:
            return jsonify({
                'error': 'Invalid input', 
                'message': str(ve)
            }), 400
    return decorated_function

@app.route('/user/followers/count', methods=['GET'])
@handle_db_errors
def count_user_followers():
    # Validate user_id parameter
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({
            'error': 'Missing user_id parameter'
        }), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({
            'error': 'Invalid user_id format'
        }), 400
    
    # Establish database connection
    connection = get_db_connection()
    if not connection:
        return jsonify({
            'error': 'Database connection failed'
        }), 500
    
    try:
        # Create cursor
        cursor = connection.cursor()
        
        # Query to count total followers
        query = """
        SELECT COUNT(*) AS total_followers 
        FROM followers 
        WHERE followed_id = %s
        """
        
        # Execute query
        cursor.execute(query, (user_id,))
        
        # Fetch result
        result = cursor.fetchone()
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
        # Return follower count
        return jsonify({
            'user_id': user_id,
            'total_followers': result[0]
        }), 200
    
    except Error as e:
        # Ensure connection is closed in case of error
        if connection:
            connection.close()
        
        app.logger.error(f"Error counting followers: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve follower count',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```