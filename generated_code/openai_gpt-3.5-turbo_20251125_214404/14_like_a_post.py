```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Create like record endpoint
@app.route('/like', methods=['POST'])
def create_like():
    user_id = request.json.get('user_id')
    post_id = request.json.get('post_id')

    if not user_id or not post_id:
        return jsonify({'error': 'Missing user_id or post_id'}), 400

    try:
        cursor.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        db.commit()
        return jsonify({'message': 'Like record created successfully'}), 200
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': 'Database error: {}'.format(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint at `/like` that accepts POST requests with JSON data containing `user_id` and `post_id` parameters. It then inserts a new record into the `likes` table in the database. Proper error handling is included for database operations.