```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="mydatabase")
cursor = db.cursor()

# Route to add a new comment to a post
@app.route('/add_comment', methods=['POST'])
def add_comment():
    post_id = request.form.get('post_id')
    user_id = request.form.get('user_id')
    content = request.form.get('content')

    if not post_id or not user_id or not content:
        return jsonify({'error': 'Missing parameters'})

    try:
        cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)", (post_id, user_id, content))
        db.commit()
        return jsonify({'message': 'Comment added successfully'})
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "mydatabase" with your actual MySQL database credentials. This code creates a Flask endpoint at `/add_comment` that accepts POST requests with parameters `post_id`, `user_id`, and `content`. It then inserts a new comment into the `comments` table in the database. Proper error handling is included to handle any database errors.