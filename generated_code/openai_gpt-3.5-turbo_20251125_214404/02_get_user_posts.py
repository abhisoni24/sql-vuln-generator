```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to retrieve posts by user_id
@app.route('/posts/<int:user_id>', methods=['GET'])
def get_posts_by_user(user_id):
    try:
        cursor.execute("SELECT * FROM posts WHERE user_id = %s", (user_id,))
        posts = cursor.fetchall()
        if posts:
            post_list = []
            for post in posts:
                post_dict = {
                    'post_id': post[0],
                    'user_id': post[1],
                    'content': post[2],
                    'created_at': post[3].strftime('%Y-%m-%d %H:%M:%S')
                }
                post_list.append(post_dict)
            return jsonify({'posts': post_list})
        else:
            return jsonify({'message': 'No posts found for user_id {}'.format(user_id)})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint that accepts a user_id parameter and retrieves all posts created by that user from the database. It returns a JSON response with the list of posts or an error message if something goes wrong.