```python
from flask import Blueprint, request, jsonify
import MySQLdb
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

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

@comments_bp.route('/comments/add', methods=['POST'])
@jwt_required()
def add_comment():
    try:
        # Get current authenticated user ID
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        post_id = data.get('post_id')
        content = data.get('content')

        # Validate input
        if not post_id or not content:
            return jsonify({
                'error': 'Missing required parameters', 
                'status': 400
            }), 400

        # Validate content length 
        if len(content) > 500:
            return jsonify({
                'error': 'Comment too long (max 500 characters)', 
                'status': 400
            }), 400

        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'error': 'Database connection failed', 
                'status': 500
            }), 500

        cursor = conn.cursor()

        # Verify post exists
        cursor.execute("""
            SELECT post_id FROM posts 
            WHERE post_id = %s
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            conn.close()
            return jsonify({
                'error': 'Post does not exist', 
                'status': 404
            }), 404

        # Insert new comment
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO comments 
            (post_id, user_id, content, created_at) 
            VALUES (%s, %s, %s, %s)
        """, (post_id, current_user_id, content, current_time))
        
        # Get the ID of the newly inserted comment
        comment_id = cursor.lastrowid

        # Commit transaction
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Comment added successfully',
            'comment_id': comment_id,
            'status': 201
        }), 201

    except MySQLdb.Error as e:
        # Rollback in case of database error
        if 'conn' in locals() and conn:
            conn.rollback()
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