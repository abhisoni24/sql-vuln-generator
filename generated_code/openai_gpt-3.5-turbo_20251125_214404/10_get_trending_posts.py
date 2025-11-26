```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to retrieve posts ordered by like count from the last 7 days
@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        # Query to retrieve posts ordered by like count from the last 7 days
        query = """
        SELECT p.post_id, p.content, COUNT(l.like_id) as like_count
        FROM posts p
        LEFT JOIN likes l ON p.post_id = l.post_id
        WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY p.post_id
        ORDER BY like_count DESC
        """
        
        cursor.execute(query)
        posts = cursor.fetchall()
        
        # Convert query result to JSON format
        posts_json = []
        for post in posts:
            post_data = {
                'post_id': post[0],
                'content': post[1],
                'like_count': post[2]
            }
            posts_json.append(post_data)
        
        return jsonify(posts_json)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code snippet creates a Flask endpoint that retrieves posts ordered by like count from the last 7 days using MySQLdb for database operations. It includes proper error handling and returns JSON responses.