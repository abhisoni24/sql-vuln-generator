```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to delete a message from the database
@app.route('/delete_message', methods=['POST'])
def delete_message():
    try:
        message_id = request.json['message_id']

        # Check if message_id is provided
        if not message_id:
            return jsonify({'error': 'Message ID is required'}), 400

        # Delete message from messages table
        cursor.execute("DELETE FROM messages WHERE message_id = %s", (message_id,))
        db.commit()

        return jsonify({'message': 'Message deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint `/delete_message` that accepts a POST request with a JSON body containing the `message_id` parameter. It then deletes the message with the provided `message_id` from the `messages` table in the database. Proper error handling is included, and JSON responses are returned.