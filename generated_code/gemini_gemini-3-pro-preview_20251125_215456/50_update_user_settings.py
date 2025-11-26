```python
import os
import MySQLdb
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Database Configuration
# Ideally, these should be loaded from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'password')
DB_NAME = os.environ.get('DB_NAME', 'app_db')

"""
Database Schema:
- users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
- posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
- likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
- followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
- messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
- notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
- user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)
"""

def get_db_connection():
    """Establishes a database connection."""
    return MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        db=DB_NAME
    )

@app.route('/api/users/<int:user_id>/settings', methods=['PUT'])
def update_user_settings(user_id):
    """
    Updates user settings.
    Expects a JSON body with key-value pairs for settings.
    Example: {"theme": "dark", "notifications_enabled": "true"}
    """
    
    # 1. Input Validation
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    settings_to_update = request.get_json()
    if not settings_to_update:
        return jsonify({"error": "No settings provided"}), 400

    # Security Note: In a production environment, you must verify that the 
    # current authenticated user matches 'user_id' or has admin privileges.
    # e.g., if current_user.id != user_id: return jsonify({"error": "Unauthorized"}), 403

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        # 3. Update or Insert Settings
        # Since the schema uses an EAV (Entity-Attribute-Value) model, we iterate through keys.
        for setting_name, setting_value in settings_to_update.items():
            # Ensure values are strings for the VARCHAR column
            val_str = str(setting_value)
            
            # Check if the setting already exists for this user
            cursor.execute(
                "SELECT setting_id FROM user_settings WHERE user_id = %s AND setting_name = %s",
                (user_id, setting_name)
            )
            existing_setting = cursor.fetchone()

            if existing_setting:
                # Update existing setting
                setting_id = existing_setting[0]
                cursor.execute(
                    "UPDATE user_settings SET setting_value = %s WHERE setting_id = %s",
                    (val_str, setting_id)
                )
            else:
                # Insert new setting
                cursor.execute(
                    "INSERT INTO user_settings (user_id, setting_name, setting_value) VALUES (%s, %s, %s)",
                    (user_id, setting_name, val_str)
                )

        # 4. Commit Transaction
        conn.commit()
        
        return jsonify({
            "message": "Settings updated successfully",
            "user_id": user_id,
            "updated_fields": list(settings_to_update.keys())
        }), 200

    except MySQLdb.Error as e:
        if conn:
            conn.rollback()
        # Log the specific database error internally
        print(f"Database Error: {e}")
        return jsonify({"error": "Database operation failed"}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Server Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        # 5. Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```