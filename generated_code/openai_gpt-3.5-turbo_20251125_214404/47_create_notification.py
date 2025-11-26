```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Create a new notification
@app.route('/create_notification', methods=['POST'])
def create_notification():
    try:
        user_id = request.json['user_id']
        notification_type = request.json['type']
        message = request.json['message']

        # Insert notification into database
        cursor.execute("INSERT INTO notifications (user_id, type, message, read, created_at) VALUES (%s, %s, %s, %s, NOW())",
                       (user_id, notification_type, message, False))
        db.commit()

        return jsonify({'message': 'Notification created successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint at `/create_notification` that accepts POST requests with JSON data containing `user_id`, `type`, and `message` parameters. It then inserts a new notification into the `notifications` table in the database. Proper error handling is included, and JSON responses are returned.