```python
from flask import Blueprint, jsonify, request
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

comments_bp = Blueprint('comments', __name__)

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
        raise BadRequest(f"Database connection error: {str(e)}")

@comments_bp.route('/comments/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    """
    Retrieve all comments for a specific post
    
    Args:
        post_id (int): Unique identifier for the post
    
    Returns:
        JSON response with comments or error message
    """
    try:
        # Validate post_id 
        if not post_id:
            return jsonify({"error": "Invalid post ID"}), 400
        
        # Get current user's ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to fetch comments with user details
        query = """
        SELECT 
            c.comment_id, 
            c.content, 
            c.created_at, 
            u.username, 
            u.user_id
        FROM 
            comments c
        JOIN 
            users u ON c.user_id = u.user_id
        WHERE 
            c.post_id = %s
        ORDER BY 
            c.created_at DESC
        """
        
        # Execute query
        cursor.execute(query, (post_id,))
        comments = cursor.fetchall()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        # Return comments
        return jsonify({
            "comments": comments,
            "total_comments": len(comments)
        }), 200
    
    except MySQLdb.Error as db_error:
        # Handle database-specific errors
        return jsonify({
            "error": "Database error occurred",
            "details": str(db_error)
        }), 500
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500
```