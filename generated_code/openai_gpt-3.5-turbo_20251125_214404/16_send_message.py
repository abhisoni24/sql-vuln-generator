```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Create a new message
@app.route('/create_message', methods=['POST'])
def create_message():
    try:
        sender_id = request.json['sender_id']
        receiver_id = request.json['receiver_id']
        content = request.json['content']

        # Insert message into messages table
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)", (sender_id, receiver_id, content))
        db.commit()

        return jsonify({'message': 'Message created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint at `/create_message` that accepts sender_id, receiver_id, and content parameters in a POST request body. It then inserts the new message into the messages table in the database. Proper error handling is included, and JSON responses are returned.