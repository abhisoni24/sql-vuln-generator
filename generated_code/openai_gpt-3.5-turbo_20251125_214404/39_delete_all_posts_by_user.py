```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Flask route to delete all posts created by a user
@app.route('/delete_posts', methods=['POST'])
def delete_posts():
    try:
        user_id = request.json.get('user_id')

        # Check if user_id parameter is provided
        if not user_id:
            return jsonify({'error': 'User ID parameter is missing'}), 400

        # Delete all posts created by the user
        cursor.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
        db.commit()

        return jsonify({'message': 'All posts created by user with ID {} have been deleted'.format(user_id)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace the placeholders `username`, `password`, and `database_name` with your actual MySQL database credentials. This code snippet provides a Flask endpoint `/delete_posts` that accepts a POST request with a JSON payload containing the `user_id` parameter. It then deletes all posts created by the user with the specified `user_id` from the `posts` table in the database. Proper error handling is included, and JSON responses are returned for success and error cases.