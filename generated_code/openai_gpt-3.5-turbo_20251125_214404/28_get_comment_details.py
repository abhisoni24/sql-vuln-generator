```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to retrieve detailed comment information
@app.route('/comment', methods=['GET'])
def get_comment_info():
    comment_id = request.args.get('comment_id')

    if not comment_id:
        return jsonify({'error': 'Missing comment_id parameter'}), 400

    try:
        cursor.execute("SELECT * FROM comments WHERE comment_id = %s", (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        comment_info = {
            'comment_id': comment[0],
            'post_id': comment[1],
            'user_id': comment[2],
            'content': comment[3],
            'created_at': comment[4]
        }

        return jsonify(comment_info), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

This code creates a Flask endpoint `/comment` that accepts a `comment_id` parameter and retrieves detailed information about the comment from the database using MySQLdb. Proper error handling is included, and the response is returned in JSON format. Make sure to replace `username`, `password`, and `database` with your actual database credentials.