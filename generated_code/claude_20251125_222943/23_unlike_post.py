```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

likes_bp = Blueprint('likes', __name__)

@likes_bp.route('/remove_like', methods=['DELETE'])
@jwt_required()
def remove_like():
    """
    Endpoint to remove a like record for a specific post by the authenticated user
    
    Request Parameters:
    - post_id (int): ID of the post to remove like from
    
    Returns:
    - JSON response indicating success or failure
    """
    try:
        # Get authenticated user's ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get post_id from request parameters 
        post_id = request.args.get('post_id', type=int)
        
        # Validate input parameters
        if not post_id:
            raise BadRequest('Post ID is required')
        
        # Establish database connection
        db = MySQLdb.connect(host='localhost', 
                             user='your_username', 
                             passwd='your_password', 
                             db='social_media_db')
        cursor = db.cursor()
        
        # Check if like exists for this user and post
        cursor.execute("""
            SELECT like_id 
            FROM likes 
            WHERE user_id = %s AND post_id = %s
        """, (current_user_id, post_id))
        
        existing_like = cursor.fetchone()
        
        if not existing_like:
            cursor.close()
            db.close()
            return jsonify({
                'success': False, 
                'message': 'Like not found'
            }), 404
        
        # Remove like record
        cursor.execute("""
            DELETE FROM likes 
            WHERE user_id = %s AND post_id = %s
        """, (current_user_id, post_id))
        
        # Commit transaction
        db.commit()
        
        # Close database connections
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True, 
            'message': 'Like removed successfully'
        }), 200
    
    except MySQLdb.Error as e:
        # Handle database errors
        return jsonify({
            'success': False, 
            'message': f'Database error: {str(e)}'
        }), 500
    
    except BadRequest as e:
        # Handle bad request errors
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 400
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'success': False, 
            'message': f'Unexpected error: {str(e)}'
        }), 500
```