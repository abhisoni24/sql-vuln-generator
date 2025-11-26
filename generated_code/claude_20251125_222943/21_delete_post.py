```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import MySQLdb
import logging

delete_post_bp = Blueprint('delete_post', __name__)

@delete_post_bp.route('/posts/delete', methods=['DELETE'])
@jwt_required()
def delete_post():
    try:
        # Get current authenticated user
        current_user_id = get_jwt_identity()
        
        # Get post_id from request
        post_id = request.json.get('post_id', None)
        
        if not post_id:
            return jsonify({
                'error': 'Post ID is required',
                'status': 400
            }), 400
        
        # Database connection
        db = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db'
        )
        cursor = db.cursor()
        
        # Verify post ownership before deletion
        cursor.execute("""
            SELECT user_id FROM posts 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        post = cursor.fetchone()
        
        if not post:
            cursor.close()
            db.close()
            return jsonify({
                'error': 'Post not found or unauthorized',
                'status': 403
            }), 403
        
        # Delete related comments
        cursor.execute("""
            DELETE FROM comments 
            WHERE post_id = %s
        """, (post_id,))
        
        # Delete related likes
        cursor.execute("""
            DELETE FROM likes 
            WHERE post_id = %s
        """, (post_id,))
        
        # Delete the post
        cursor.execute("""
            DELETE FROM posts 
            WHERE post_id = %s
        """, (post_id,))
        
        # Commit changes
        db.commit()
        
        # Close database connections
        cursor.close()
        db.close()
        
        return jsonify({
            'message': 'Post deleted successfully',
            'status': 200
        }), 200
    
    except MySQLdb.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({
            'error': 'Database error occurred',
            'status': 500
        }), 500
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500
```