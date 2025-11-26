```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to remove follow relationship
@app.route('/remove_follow', methods=['POST'])
def remove_follow():
    follower_id = request.json.get('follower_id')
    followed_id = request.json.get('followed_id')

    if not follower_id or not followed_id:
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Check if the follow relationship exists
        cursor.execute("SELECT * FROM followers WHERE follower_id = %s AND followed_id = %s", (follower_id, followed_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Follow relationship does not exist'}), 404

        # Remove the follow relationship
        cursor.execute("DELETE FROM followers WHERE follower_id = %s AND followed_id = %s", (follower_id, followed_id))
        db.commit()

        return jsonify({'message': 'Follow relationship removed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL credentials and database name. This code creates a Flask endpoint `/remove_follow` that accepts POST requests with JSON data containing `follower_id` and `followed_id` parameters. It checks if the follow relationship exists and removes it from the `followers` table in the database. Proper error handling is included, and JSON responses are returned.