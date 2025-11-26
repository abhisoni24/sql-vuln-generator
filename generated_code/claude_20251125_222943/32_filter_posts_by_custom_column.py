```python
from flask import Flask, request, jsonify
import MySQLdb
import os
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'), 
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME')
        )
        return conn
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

@app.route('/filter_posts', methods=['GET'])
def filter_posts():
    try:
        # Validate input parameters 
        column_name = request.args.get('column_name')
        value = request.args.get('value')

        # Validate parameters are not empty
        if not column_name or not value:
            raise BadRequest("Column name and value are required")

        # Whitelist allowed columns to prevent SQL injection
        allowed_columns = ['user_id', 'content']
        if column_name not in allowed_columns:
            raise BadRequest("Invalid column name")

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Prepare and execute parameterized query
        query = f"SELECT * FROM posts WHERE {column_name} = %s"
        cursor.execute(query, (value,))
        
        # Fetch results
        posts = cursor.fetchall()

        # Close database connections
        cursor.close()
        conn.close()

        # Return filtered posts
        return jsonify({
            'status': 'success', 
            'posts': posts
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
            'message': 'Database query failed'
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'An unexpected error occurred'
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```