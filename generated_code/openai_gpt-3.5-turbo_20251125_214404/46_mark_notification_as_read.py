```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to mark a notification as read
@app.route('/mark_notification_as_read', methods=['POST'])
def mark_notification_as_read():
    try:
        notification_id = request.json['notification_id']
        
        # Update notification as read in the database
        cursor.execute("UPDATE notifications SET read = 1 WHERE notification_id = %s", (notification_id,))
        db.commit()
        
        return jsonify({'message': 'Notification marked as read successfully'})
    
    except KeyError:
        return jsonify({'error': 'Missing notification_id parameter'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint `/mark_notification_as_read` that accepts a POST request with a JSON body containing the `notification_id` parameter. It then updates the corresponding notification in the database to mark it as read. Proper error handling is included to handle missing parameters or any other exceptions that may occur.