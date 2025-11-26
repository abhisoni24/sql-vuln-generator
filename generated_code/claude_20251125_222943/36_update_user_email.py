```python
from flask import Flask, request, jsonify
import MySQLdb
import re
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Database connection configuration
def get_db_connection():
    try:
        conn = MySQLdb.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'), 
            passwd=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME')
        )
        return conn
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return None

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

@app.route('/users/update_email', methods=['PUT'])
@jwt_required()
def update_user_email():
    """
    Update user email endpoint
    Requires JWT authentication
    """
    try:
        # Get current authenticated user ID 
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        new_email = data.get('email', '').strip()

        # Validate email
        if not new_email:
            return jsonify({"error": "Email is required"}), 400
        
        if not validate_email(new_email):
            return jsonify({"error": "Invalid email format"}), 400

        # Database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (new_email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({"error": "Email already in use"}), 409

        # Update email
        cursor.execute("""
            UPDATE users 
            SET email = %s 
            WHERE user_id = %s
        """, (new_email, current_user_id))
        
        # Commit changes
        conn.commit()
        
        # Close database connections
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Email updated successfully",
            "user_id": current_user_id
        }), 200

    except MySQLdb.Error as db_error:
        # Database specific error handling
        return jsonify({
            "error": "Database error occurred",
            "details": str(db_error)
        }), 500
    
    except Exception as e:
        # Generic error handling
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.run(debug=True)
```