```python
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    try:
        # Get authenticated user's ID 
        current_user_id = get_jwt_identity()
        
        # Optional query parameters for pagination and filtering
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        read_status = request.args.get('read', default=None, type=str)

        # Validate pagination parameters
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        offset = (page - 1) * per_page

        # Establish database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Build dynamic query based on read status
        query = """
        SELECT notification_id, type, message, read, created_at 
        FROM notifications 
        WHERE user_id = %s
        """
        params = [current_user_id]

        if read_status is not None:
            query += " AND read = %s"
            params.append(read_status.lower() == 'true')

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        notifications = cursor.fetchall()

        # Count total notifications for pagination metadata
        count_query = """
        SELECT COUNT(*) as total 
        FROM notifications 
        WHERE user_id = %s
        """
        count_params = [current_user_id]
        
        if read_status is not None:
            count_query += " AND read = %s"
            count_params.append(read_status.lower() == 'true')

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            "notifications": notifications,
            "page": page,
            "per_page": per_page,
            "total_count": total_count
        }), 200

    except MySQLdb.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
```