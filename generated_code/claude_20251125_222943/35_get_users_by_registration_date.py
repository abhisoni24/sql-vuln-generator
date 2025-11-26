```python
from flask import Flask, request, jsonify
import MySQLdb
from datetime import datetime
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'passwd': 'your_password', 
    'db': 'social_network_db'
}

# Rate limiting configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)

@app.route('/api/users/date-range', methods=['GET'])
@limiter.limit("10 per minute")
def get_users_by_date_range():
    """
    Retrieve users registered within a specific date range
    
    Query Parameters:
    - start_date: Start date for user registration (YYYY-MM-DD)
    - end_date: End date for user registration (YYYY-MM-DD)
    """
    try:
        # Validate and parse input parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Input validation
        if not start_date or not end_date:
            return jsonify({
                'error': 'Missing start_date or end_date parameters',
                'status': 400
            }), 400

        try:
            # Validate date format
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD',
                'status': 400
            }), 400

        # Establish database connection
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Parameterized query to prevent SQL injection
        query = """
        SELECT user_id, username, email, bio, created_at 
        FROM users 
        WHERE created_at BETWEEN %s AND %s
        ORDER BY created_at ASC
        """

        # Execute query with parameters
        cursor.execute(query, (start_date, end_date))
        users = cursor.fetchall()

        # Close database connections
        cursor.close()
        conn.close()

        # Return results
        return jsonify({
            'users': users,
            'count': len(users),
            'status': 200
        }), 200

    except MySQLdb.Error as db_error:
        # Handle database-specific errors
        return jsonify({
            'error': f'Database error: {str(db_error)}',
            'status': 500
        }), 500

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'status': 500
        }), 500

# Error handler for rate limiting
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded. Please try again later.',
        'status': 429
    }), 429

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```