```python
from flask import Blueprint, request, jsonify
import MySQLdb
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

user_delete_bp = Blueprint('user_delete', __name__)

@user_delete_bp.route('/delete_user', methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        # Get current authenticated user
        current_user_id = get_jwt_identity()
        
        # Get request parameters 
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')

        # Validate input
        if not user_id or not password:
            return jsonify({"error": "User ID and password are required"}), 400

        # Database connection
        db = MySQLdb.connect(host='localhost', 
                              user='your_username', 
                              passwd='your_password', 
                              db='social_media_db')
        cursor = db.cursor()

        # Verify user credentials before deletion
        cursor.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if not result or not check_password_hash(result[0], password):
            cursor.close()
            db.close()
            return jsonify({"error": "Invalid credentials"}), 401

        # Ensure user can only delete their own account
        if int(current_user_id) != int(user_id):
            cursor.close()
            db.close()
            return jsonify({"error": "Unauthorized deletion"}), 403

        # Begin transaction for cascading deletes
        db.begin()

        # Delete related records in other tables
        tables_to_delete = [
            'posts', 
            'comments', 
            'likes', 
            'followers', 
            'messages', 
            'notifications', 
            'user_settings'
        ]

        for table in tables_to_delete:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))

        # Delete user record
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

        # Commit transaction
        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "User deleted successfully"}), 200

    except MySQLdb.Error as e:
        # Rollback transaction on error
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```