```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to remove a like record
@app.route('/remove_like', methods=['POST'])
def remove_like():
    try:
        user_id = request.json['user_id']
        post_id = request.json['post_id']

        # Check if the like record exists
        cursor.execute("SELECT * FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
        like = cursor.fetchone()

        if like:
            # Remove the like record
            cursor.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
            db.commit()
            return jsonify({'message': 'Like record removed successfully'})
        else:
            return jsonify({'error': 'Like record not found'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint `/remove_like` that accepts POST requests with JSON data containing `user_id` and `post_id` parameters. It checks if the like record exists in the database and removes it if found. Proper error handling is included, and JSON responses are returned.