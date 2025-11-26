```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to retrieve most recent messages
@app.route('/messages', methods=['GET'])
def get_recent_messages():
    try:
        limit = request.args.get('limit', default=10, type=int)

        query = "SELECT * FROM messages ORDER BY created_at DESC LIMIT %s"
        cursor.execute(query, (limit,))
        messages = cursor.fetchall()

        message_list = []
        for message in messages:
            message_dict = {
                'message_id': message[0],
                'sender_id': message[1],
                'receiver_id': message[2],
                'content': message[3],
                'created_at': message[4].strftime('%Y-%m-%d %H:%M:%S')
            }
            message_list.append(message_dict)

        return jsonify({'messages': message_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL credentials and database name. This code creates a Flask endpoint at `/messages` that retrieves the most recent messages based on the provided limit parameter. It handles errors and returns JSON responses.