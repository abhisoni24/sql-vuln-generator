```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

delete_posts_bp = Blueprint('delete_posts', __name__)

@delete_posts_bp.route('/delete_user_posts', methods=['DELETE'])
@jwt_required()
def delete_user_posts():
    try:
        # Get authenticated user's ID
        current_user_id = get_jwt_identity()
        
        # Get target user_id from request parameters
        target_user_id = request.args.get('user_id', type=int)
        
        # Validate input
        if not target_user_id:
            raise BadRequest('User ID is required')
        
        # Ensure user can only delete their own posts
        if current_user_id != target_user_id:
            return jsonify({'error': 'Unauthorized to delete posts'}), 403
        
        # Database connection
        db = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db'
        )
        cursor = db.cursor()
        
        # Start transaction
        db.begin()
        
        try:
            # Delete associated likes first to maintain referential integrity
            delete_likes_query = """
            DELETE FROM likes 
            WHERE post_id IN (
                SELECT post_id FROM posts 
                WHERE user_id = %s
            )
            """
            cursor.execute(delete_likes_query, (target_user_id,))
            
            # Delete associated comments 
            delete_comments_query = """
            DELETE FROM comments 
            WHERE post_id IN (
                SELECT post_id FROM posts 
                WHERE user_id = %s
            )
            """
            cursor.execute(delete_comments_query, (target_user_id,))
            
            # Delete posts
            delete_posts_query = """
            DELETE FROM posts 
            WHERE user_id = %s
            """
            cursor.execute(delete_posts_query, (target_user_id,))
            
            # Commit transaction
            db.commit()
            
            return jsonify({
                'message': f'Successfully deleted all posts for user {target_user_id}',
                'deleted_posts_count': cursor.rowcount
            }), 200
        
        except MySQLdb.Error as e:
            # Rollback in case of error
            db.rollback()
            return jsonify({
                'error': 'Database error occurred', 
                'details': str(e)
            }), 500
        
        finally:
            # Close database connections
            cursor.close()
            db.close()
    
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred', 
            'details': str(e)
        }), 500
```