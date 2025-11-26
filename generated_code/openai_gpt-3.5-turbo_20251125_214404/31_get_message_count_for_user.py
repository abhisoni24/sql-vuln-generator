```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to count total messages for a specific user
@app.route('/count_messages', methods=['GET'])
def count_messages():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    try:
        cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = %s", (user_id,))
        total_messages = cursor.fetchone()[0]
        return jsonify({'user_id': user_id, 'total_messages': total_messages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at `/count_messages` that accepts a `user_id` parameter and returns the total number of messages received by that user. It uses MySQLdb for database operations and includes proper error handling.