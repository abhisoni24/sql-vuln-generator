```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

posts_bp = Blueprint('posts', __name__)

def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db',
            charset='utf8mb4'
        )
        return conn
    except MySQLdb.Error as e:
        raise Exception(f"Database connection error: {str(e)}")

@posts_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    try:
        # Get current user from JWT token
        current_user_id = get_jwt_identity()
        
        # Validate request data
        data = request.get_json()
        if not data or 'content' not in data:
            raise BadRequest('Content is required')
        
        new_content = data['content']
        
        # Validate content length 
        if len(new_content) > 5000:
            raise BadRequest('Content exceeds maximum length')
        
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if post exists and belongs to current user
        cursor.execute("""
            SELECT user_id FROM posts 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        post = cursor.fetchone()
        if not post:
            cursor.close()
            conn.close()
            return jsonify({
                'error': 'Post not found or unauthorized',
                'status': 403
            }), 403
        
        # Update post content
        cursor.execute("""
            UPDATE posts 
            SET content = %s 
            WHERE post_id = %s AND user_id = %s
        """, (new_content, post_id, current_user_id))
        
        # Commit changes
        conn.commit()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Post updated successfully',
            'post_id': post_id,
            'status': 200
        }), 200
    
    except BadRequest as e:
        return jsonify({
            'error': str(e),
            'status': 400
        }), 400
    
    except MySQLdb.Error as e:
        return jsonify({
            'error': f'Database error: {str(e)}',
            'status': 500
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'status': 500
        }), 500
```