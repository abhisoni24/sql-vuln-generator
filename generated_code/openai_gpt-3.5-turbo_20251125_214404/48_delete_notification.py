```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to delete a notification
@app.route('/delete_notification', methods=['POST'])
def delete_notification():
    try:
        notification_id = request.json.get('notification_id')

        if not notification_id:
            return jsonify({'error': 'Notification ID is required'}), 400

        # Delete notification from database
        cursor.execute("DELETE FROM notifications WHERE notification_id = %s", (notification_id,))
        db.commit()

        return jsonify({'message': 'Notification deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

This code creates a Flask endpoint `/delete_notification` that accepts a POST request with a JSON body containing the `notification_id` parameter. It then deletes the notification with the specified `notification_id` from the `notifications` table in the MySQL database.

Make sure to replace `username`, `password`, and `database` with your MySQL database credentials.