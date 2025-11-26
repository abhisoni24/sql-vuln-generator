```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """
    Delete a comment by its ID
    Requires JWT authentication
    Ensures user can only delete their own comments
    """
    try:
        # Get authenticated user's ID 
        current_user_id = get_jwt_identity()

        # Establish database connection
        db = MySQLdb.connect(host='localhost', 
                             user='your_username', 
                             passwd='your_password', 
                             db='social_media_db')
        cursor = db.cursor()

        # First verify comment exists and belongs to current user
        cursor.execute("""
            SELECT user_id 
            FROM comments 
            WHERE comment_id = %s
        """, (comment_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            db.close()
            return jsonify({"error": "Comment not found"}), 404
        
        # Check if current user owns the comment
        if result[0] != current_user_id:
            cursor.close()
            db.close()
            return jsonify({"error": "Unauthorized to delete this comment"}), 403

        # Delete the comment
        cursor.execute("""
            DELETE FROM comments 
            WHERE comment_id = %s
        """, (comment_id,))
        
        # Commit transaction
        db.commit()

        # Close database connections
        cursor.close()
        db.close()

        return jsonify({"message": "Comment deleted successfully"}), 200

    except MySQLdb.Error as e:
        # Handle database specific errors
        return jsonify({
            "error": "Database error", 
            "details": str(e)
        }), 500
    
    except BadRequest as e:
        # Handle bad request errors
        return jsonify({
            "error": "Bad request", 
            "details": str(e)
        }), 400
    
    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            "error": "Unexpected error", 
            "details": str(e)
        }), 500
```