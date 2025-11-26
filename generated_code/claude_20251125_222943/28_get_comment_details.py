```python
from flask import Blueprint, jsonify, request
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

comments_bp = Blueprint('comments', __name__)

def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='your_username', 
            passwd='your_password',
            db='social_media_db',
            charset='utf8mb4'
        )
        return connection
    except MySQLdb.Error as e:
        raise BadRequest(f"Database connection error: {str(e)}")

@comments_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment_details(comment_id):
    """
    Retrieve detailed comment information by comment_id
    
    Args:
        comment_id (int): Unique identifier for the comment
    
    Returns:
        JSON response with comment details
    """
    current_user_id = get_jwt_identity()
    
    try:
        # Establish database connection
        connection = get_db_connection()
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to fetch comment details with related user and post information
        query = """
        SELECT 
            c.comment_id, 
            c.content AS comment_content, 
            c.created_at AS comment_timestamp,
            u.user_id, 
            u.username,
            p.post_id,
            p.content AS post_content
        FROM 
            comments c
        JOIN 
            users u ON c.user_id = u.user_id
        JOIN 
            posts p ON c.post_id = p.post_id
        WHERE 
            c.comment_id = %s
        """
        
        # Execute query
        cursor.execute(query, (comment_id,))
        comment_details = cursor.fetchone()
        
        # Close database connections
        cursor.close()
        connection.close()
        
        # Handle comment not found
        if not comment_details:
            return jsonify({
                'error': 'Comment not found',
                'status': 404
            }), 404
        
        return jsonify({
            'status': 'success',
            'comment': comment_details
        }), 200
    
    except MySQLdb.Error as db_error:
        return jsonify({
            'error': f'Database error: {str(db_error)}',
            'status': 500
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'status': 500
        }), 500
```