```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/delete_user_comments', methods=['DELETE'])
@jwt_required()
def delete_user_comments():
    """
    Delete all comments created by a specific user
    Requires JWT authentication
    """
    try:
        # Get current authenticated user's ID 
        current_user_id = get_jwt_identity()
        
        # Get target user_id from request parameters
        target_user_id = request.args.get('user_id', type=int)
        
        # Validate input
        if not target_user_id:
            raise BadRequest('User ID is required')
        
        # Prevent users from deleting comments for other users
        if current_user_id != target_user_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You can only delete your own comments'
            }), 403
        
        # Database connection
        db = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db'
        )
        cursor = db.cursor()
        
        # Delete comments for the specified user
        delete_query = """
        DELETE FROM comments 
        WHERE user_id = %s
        """
        
        cursor.execute(delete_query, (target_user_id,))
        db.commit()
        
        # Get number of deleted comments
        deleted_count = cursor.rowcount
        
        # Close database connections
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} comments',
            'deleted_count': deleted_count
        }), 200
    
    except MySQLdb.Error as e:
        # Database-specific error handling
        return jsonify({
            'error': 'Database Error',
            'message': str(e)
        }), 500
    
    except BadRequest as e:
        # Input validation error
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
```