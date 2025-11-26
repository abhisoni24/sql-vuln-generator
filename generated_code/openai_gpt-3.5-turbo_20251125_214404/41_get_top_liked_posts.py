```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to retrieve posts with the highest like counts
@app.route('/posts', methods=['GET'])
def get_posts_with_highest_likes():
    try:
        limit = request.args.get('limit', type=int)
        if limit is None:
            return jsonify({'error': 'Limit parameter is required'}), 400

        query = "SELECT p.post_id, p.content, COUNT(l.like_id) AS like_count " \
                "FROM posts p " \
                "LEFT JOIN likes l ON p.post_id = l.post_id " \
                "GROUP BY p.post_id " \
                "ORDER BY like_count DESC " \
                "LIMIT %s"
        
        cursor.execute(query, (limit,))
        posts = cursor.fetchall()

        result = []
        for post in posts:
            post_data = {
                'post_id': post[0],
                'content': post[1],
                'like_count': post[2]
            }
            result.append(post_data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace the placeholders for MySQL connection details with your actual database credentials. This code snippet creates a Flask endpoint that retrieves posts with the highest like counts based on the provided limit parameter. It uses MySQLdb for database operations and returns JSON responses with proper error handling.