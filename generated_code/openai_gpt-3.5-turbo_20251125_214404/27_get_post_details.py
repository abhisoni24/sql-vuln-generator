```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to retrieve detailed post information
@app.route('/post', methods=['GET'])
def get_post_info():
    post_id = request.args.get('post_id')

    if not post_id:
        return jsonify({'error': 'Missing post_id parameter'}), 400

    try:
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            return jsonify({'error': 'Post not found'}), 404

        post_info = {
            'post_id': post[0],
            'user_id': post[1],
            'content': post[2],
            'created_at': post[3]
        }

        return jsonify(post_info), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint at `/post` that accepts a `post_id` parameter and retrieves detailed post information from the database. It handles errors and returns JSON responses accordingly.