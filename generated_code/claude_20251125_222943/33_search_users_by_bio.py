```python
from flask import Flask, request, jsonify
import MySQLdb
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
CORS(app)

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
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

@app.route('/api/users/search_by_bio', methods=['GET'])
def search_users_by_bio():
    try:
        # Validate keyword parameter 
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            raise BadRequest("Keyword parameter is required")
        
        # Prevent SQL injection with parameterized query
        query = """
        SELECT user_id, username, email, bio 
        FROM users 
        WHERE bio LIKE %s 
        LIMIT 50
        """
        
        # Open database connection
        connection = get_db_connection()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Execute query with parameter
        search_param = f"%{keyword}%"
        cursor.execute(query, (search_param,))
        
        # Fetch results
        results = cursor.fetchall()
        
        # Close database resources
        cursor.close()
        connection.close()
        
        # Return JSON response
        return jsonify({
            'status': 'success',
            'total_results': len(results),
            'users': results
        }), 200
    
    except BadRequest as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 400
    
    except MySQLdb.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Internal server error'
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Unexpected error occurred'
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```