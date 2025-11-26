```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import MySQLdb
import os
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest, NotFound

load_dotenv()

app = Flask(__name__)
CORS(app)

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
        raise

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            raise BadRequest("User ID is required")
        
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch user profile details
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.username, 
                u.email, 
                u.bio, 
                u.created_at,
                (SELECT COUNT(*) FROM posts p WHERE p.user_id = u.user_id) as post_count,
                (SELECT COUNT(*) FROM followers f WHERE f.followed_id = u.user_id) as followers_count,
                (SELECT COUNT(*) FROM followers f WHERE f.follower_id = u.user_id) as following_count
            FROM users u
            WHERE u.user_id = %s
        """, (user_id,))
        
        user_profile = cursor.fetchone()
        
        if not user_profile:
            raise NotFound("User profile not found")
        
        # Fetch recent posts
        cursor.execute("""
            SELECT 
                post_id, 
                content, 
                created_at,
                (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.post_id) as likes_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id) as comments_count
            FROM posts p
            WHERE p.user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        
        recent_posts = cursor.fetchall()
        
        # Combine profile and posts
        response_data = {
            "profile": user_profile,
            "recent_posts": recent_posts
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(response_data), 200
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except MySQLdb.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```