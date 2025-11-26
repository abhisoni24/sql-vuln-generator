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
    """Establish secure database connection"""
    try:
        connection = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

@app.route('/api/search/posts', methods=['GET'])
def search_posts():
    """
    Search posts containing a specific keyword
    Query Parameters:
    - keyword: Search term to find in post content
    - limit: Optional, max number of results (default 50)
    - offset: Optional, pagination offset (default 0)
    """
    try:
        # Validate and sanitize input parameters
        keyword = request.args.get('keyword', '').strip()
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        if not keyword:
            raise BadRequest("Keyword is required")

        # Establish database connection
        connection = get_db_connection()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Parameterized query to prevent SQL injection
        query = """
        SELECT 
            p.post_id, 
            p.content, 
            p.created_at, 
            u.username 
        FROM 
            posts p
        JOIN 
            users u ON p.user_id = u.user_id
        WHERE 
            p.content LIKE %s
        ORDER BY 
            p.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        search_param = f"%{keyword}%"
        cursor.execute(query, (search_param, limit, offset))
        
        results = cursor.fetchall()
        total_count = cursor.rowcount

        # Close database resources
        cursor.close()
        connection.close()

        return jsonify({
            'posts': results,
            'total_count': total_count,
            'keyword': keyword
        }), 200

    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except MySQLdb.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except ValueError:
        return jsonify({'error': 'Invalid input parameters'}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```