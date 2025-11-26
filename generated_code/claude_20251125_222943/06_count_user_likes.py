```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

@app.route('/user/total_likes', methods=['GET'])
def get_user_total_likes():
    try:
        # Validate user_id parameter 
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Missing user_id parameter', 
                'status': 400
            }), 400
        
        # Validate user_id is numeric
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                'error': 'Invalid user_id format', 
                'status': 400
            }), 400

        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'error': 'Database connection failed', 
                'status': 500
            }), 500

        cursor = conn.cursor()

        # Query to count total likes on user's posts
        query = """
        SELECT COUNT(*) as total_likes 
        FROM likes l
        JOIN posts p ON l.post_id = p.post_id
        WHERE p.user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        # Close database resources
        cursor.close()
        conn.close()

        # Return total likes count
        return jsonify({
            'user_id': user_id,
            'total_likes': result[0] if result else 0,
            'status': 200
        }), 200

    except MySQLdb.Error as db_error:
        app.logger.error(f"Database query error: {db_error}")
        return jsonify({
            'error': 'Database query failed', 
            'status': 500
        }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Internal server error', 
            'status': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```