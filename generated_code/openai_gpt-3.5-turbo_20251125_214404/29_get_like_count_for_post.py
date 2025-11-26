```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to count total likes for a specific post
@app.route('/post/likes', methods=['GET'])
def count_likes():
    post_id = request.args.get('post_id')

    if not post_id:
        return jsonify({'error': 'Missing post_id parameter'}), 400

    try:
        cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,))
        total_likes = cursor.fetchone()[0]
        return jsonify({'post_id': post_id, 'total_likes': total_likes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at `/post/likes` that accepts a `post_id` parameter and returns the total number of likes for that specific post. It handles errors gracefully and returns JSON responses.