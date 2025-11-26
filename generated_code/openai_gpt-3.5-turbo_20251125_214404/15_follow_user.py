```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to create a follow relationship
@app.route('/follow', methods=['POST'])
def create_follow_relationship():
    follower_id = request.json.get('follower_id')
    followed_id = request.json.get('followed_id')

    if not follower_id or not followed_id:
        return jsonify({'error': 'follower_id and followed_id are required'}), 400

    try:
        # Check if the follow relationship already exists
        cursor.execute("SELECT * FROM followers WHERE follower_id = %s AND followed_id = %s", (follower_id, followed_id))
        existing_relationship = cursor.fetchone()

        if existing_relationship:
            return jsonify({'error': 'Follow relationship already exists'}), 400

        # Create the follow relationship
        cursor.execute("INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s)", (follower_id, followed_id))
        db.commit()

        return jsonify({'message': 'Follow relationship created successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint at `/follow` that accepts POST requests with JSON data containing `follower_id` and `followed_id` parameters. It checks if the follow relationship already exists and creates a new relationship if it doesn't. Proper error handling is included, and JSON responses are returned.