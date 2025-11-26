```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="root", passwd="password", db="mydatabase")
cursor = db.cursor()

# Endpoint to retrieve messages for a given user_id
@app.route('/messages', methods=['GET'])
def get_messages():
    user_id = request.args.get('user_id')

    if user_id is None:
        return jsonify({'error': 'user_id parameter is required'}), 400

    try:
        # Retrieve messages where user is sender or receiver
        cursor.execute("SELECT * FROM messages WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))
        messages = cursor.fetchall()

        # Convert messages to dictionary format
        messages_list = []
        for message in messages:
            message_dict = {
                'message_id': message[0],
                'sender_id': message[1],
                'receiver_id': message[2],
                'content': message[3],
                'created_at': message[4].strftime('%Y-%m-%d %H:%M:%S')
            }
            messages_list.append(message_dict)

        return jsonify({'messages': messages_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace the MySQL connection details with your actual database credentials. This code creates a Flask endpoint `/messages` that accepts a `user_id` parameter and retrieves all messages where the user is the sender or receiver. The messages are returned in JSON format with proper error handling.