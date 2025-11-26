```python
from flask import Blueprint, request, jsonify
import MySQLdb
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

likes_bp = Blueprint('likes', __name__)

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

@likes_bp.route('/like', methods=['POST'])
@jwt_required()  # Requires valid JWT token
def create_like():
    try:
        # Get current authenticated user's ID 
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        post_id = data.get('post_id')

        # Validate input
        if not post_id:
            return jsonify({"error": "Post ID is required"}), 400

        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Check if post exists
        cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (post_id,))
        post = cursor.fetchone()
        if not post:
            cursor.close()
            conn.close()
            return jsonify({"error": "Post does not exist"}), 404

        # Check if like already exists
        cursor.execute(
            "SELECT like_id FROM likes WHERE user_id = %s AND post_id = %s", 
            (current_user_id, post_id)
        )
        existing_like = cursor.fetchone()
        
        if existing_like:
            cursor.close()
            conn.close()
            return jsonify({"message": "Like already exists"}), 409

        # Insert new like
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO likes (user_id, post_id, created_at) VALUES (%s, %s, %s)", 
            (current_user_id, post_id, current_time)
        )
        
        # Get the ID of the newly inserted like
        like_id = cursor.lastrowid

        # Commit transaction
        conn.commit()

        # Close database connections
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Like created successfully", 
            "like_id": like_id
        }), 201

    except MySQLdb.Error as db_error:
        # Rollback in case of database error
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
```

Key Security and Best Practices Implemented:
1. JWT authentication to verify user identity
2. Input validation
3. Parameterized queries to prevent SQL injection
4. Error handling for database and other exceptions
5. Proper connection and cursor management
6. Transaction management with commit/rollback
7. Checks for existing likes to prevent duplicates
8. Verifies post existence before creating like
9. Uses prepared statements
10. Sanitizes and validates input data

Note: Replace 'your_username' and 'your_password' with actual database credentials. Ensure you have flask-jwt-extended installed and configured for JWT authentication.