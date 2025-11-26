```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to retrieve comments for a post
@app.route('/post_comments', methods=['GET'])
def get_post_comments():
    post_id = request.args.get('post_id')

    if not post_id:
        return jsonify({'error': 'Missing post_id parameter'}), 400

    try:
        cursor.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
        comments = cursor.fetchall()
        if not comments:
            return jsonify({'message': 'No comments found for this post'}), 404
        else:
            return jsonify({'comments': comments}), 200
    except MySQLdb.Error as e:
        return jsonify({'error': 'Database error: {}'.format(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

This code creates a Flask endpoint `/post_comments` that accepts a `post_id` parameter in the query string. It retrieves all comments for the specified post from the `comments` table in the database using MySQLdb for database operations. Proper error handling is included to handle missing parameters and database errors. The endpoint returns JSON responses with the comments data or error messages.