```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="mydatabase")
cursor = db.cursor()

# Create a new post for a user
@app.route('/create_post', methods=['POST'])
def create_post():
    try:
        user_id = request.form.get('user_id')
        content = request.form.get('content')

        if not user_id or not content:
            return jsonify({'error': 'Missing user_id or content parameter'}), 400

        # Insert new post into the database
        cursor.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (user_id, content))
        db.commit()

        return jsonify({'message': 'Post created successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "mydatabase" with your actual MySQL database credentials. This code snippet creates a Flask endpoint at `/create_post` that accepts `user_id` and `content` parameters via a POST request. It then inserts a new post into the `posts` table in the database. Proper error handling is included, and JSON responses are returned.