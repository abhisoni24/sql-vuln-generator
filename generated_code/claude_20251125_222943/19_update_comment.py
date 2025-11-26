```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

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
        print(f"Database connection error: {e}")
        return None

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    # Get current user's ID from JWT token
    current_user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    
    # Validate input
    if not data or 'content' not in data:
        return jsonify({
            'error': 'Missing content parameter', 
            'status': 400
        }), 400
    
    new_content = data['content']
    
    # Validate content length 
    if len(new_content) > 500:
        return jsonify({
            'error': 'Comment too long (max 500 characters)', 
            'status': 400
        }), 400
    
    # Database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'error': 'Database connection failed', 
            'status': 500
        }), 500
    
    cursor = conn.cursor()
    
    try:
        # First verify comment ownership
        cursor.execute("""
            SELECT user_id FROM comments 
            WHERE comment_id = %s
        """, (comment_id,))
        
        result = cursor.fetchone()
        
        # Check if comment exists
        if not result:
            conn.close()
            return jsonify({
                'error': 'Comment not found', 
                'status': 404
            }), 404
        
        # Check if current user owns the comment
        if result[0] != current_user_id:
            conn.close()
            return jsonify({
                'error': 'Unauthorized to update this comment', 
                'status': 403
            }), 403
        
        # Update comment
        cursor.execute("""
            UPDATE comments 
            SET content = %s 
            WHERE comment_id = %s
        """, (new_content, comment_id))
        
        # Commit transaction
        conn.commit()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Comment updated successfully', 
            'comment_id': comment_id,
            'status': 200
        }), 200
    
    except MySQLdb.Error as e:
        # Rollback in case of error
        conn.rollback()
        
        # Close database connections
        cursor.close()
        conn.close()
        
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