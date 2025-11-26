```python
from flask import Blueprint, request, jsonify
import MySQLdb
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create blueprint for posts
posts_bp = Blueprint('posts', __name__)

# Database connection configuration
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

@posts_bp.route('/create_post', methods=['POST'])
@jwt_required()  # Requires valid JWT token
def create_post():
    try:
        # Get current authenticated user's ID
        current_user_id = get_jwt_identity()
        
        # Get post content from request
        data = request.get_json()
        
        # Validate input
        if not data or 'content' not in data:
            return jsonify({
                'error': 'Content is required', 
                'status': 400
            }), 400
        
        content = data['content']
        
        # Validate content length 
        if len(content) > 1000:
            return jsonify({
                'error': 'Post content too long (max 1000 characters)', 
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
        
        # Verify user exists
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (current_user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'error': 'User not found', 
                'status': 404
            }), 404
        
        # Insert new post
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO posts (user_id, content, created_at) 
            VALUES (%s, %s, %s)
        """, (current_user_id, content, current_time))
        
        # Get the ID of the newly created post
        new_post_id = cursor.lastrowid
        
        # Commit transaction
        conn.commit()
        
        # Close database connections
        cursor.close()
        conn.close()
        
        # Return success response
        return jsonify({
            'message': 'Post created successfully',
            'post_id': new_post_id,
            'status': 201
        }), 201
    
    except MySQLdb.Error as db_error:
        # Handle database-specific errors
        return jsonify({
            'error': f'Database error: {str(db_error)}', 
            'status': 500
        }), 500
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            'error': f'Unexpected error: {str(e)}', 
            'status': 500
        }), 500
```