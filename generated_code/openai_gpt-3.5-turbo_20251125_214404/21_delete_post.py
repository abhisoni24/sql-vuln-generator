```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to delete a post by post_id
@app.route('/delete_post', methods=['POST'])
def delete_post():
    post_id = request.json.get('post_id')

    if not post_id:
        return jsonify({'error': 'Missing post_id parameter'}), 400

    try:
        # Delete post from posts table
        cursor.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
        db.commit()
        return jsonify({'message': 'Post deleted successfully'})
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': 'Failed to delete post', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at `/delete_post` that accepts a POST request with a JSON body containing the `post_id` parameter. It then deletes the post with the specified `post_id` from the `posts` table in the database. Proper error handling is included to handle any database errors that may occur.