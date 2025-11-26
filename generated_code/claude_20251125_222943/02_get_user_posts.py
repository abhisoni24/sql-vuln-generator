```python
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'social_network_db'

mysql = MySQL(app)

@app.route('/user/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """
    Retrieve all posts created by a specific user
    
    Parameters:
    - user_id (int): Unique identifier for the user
    
    Returns:
    - JSON array of user's posts
    """
    try:
        # Validate user_id is positive 
        if user_id <= 0:
            raise BadRequest("Invalid user ID")
        
        # Create database cursor
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if user exists first
        cur.execute("SELECT COUNT(*) as user_count FROM users WHERE user_id = %s", (user_id,))
        user_check = cur.fetchone()
        
        if user_check['user_count'] == 0:
            raise NotFound("User not found")
        
        # Retrieve user posts with additional details
        cur.execute("""
            SELECT 
                post_id, 
                content, 
                created_at,
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) as like_count,
                (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) as comment_count
            FROM posts 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        posts = cur.fetchall()
        
        # Close cursor
        cur.close()
        
        # Return posts as JSON response
        return jsonify({
            'user_id': user_id,
            'posts': posts,
            'total_posts': len(posts)
        }), 200
    
    except MySQLdb.Error as e:
        # Handle database-specific errors
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500
    
    except BadRequest as e:
        # Handle invalid input errors
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    
    except NotFound as e:
        # Handle user not found
        return jsonify({
            'error': 'Not Found',
            'message': str(e)
        }), 404
    
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```