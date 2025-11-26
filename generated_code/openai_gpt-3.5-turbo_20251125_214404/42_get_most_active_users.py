```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to retrieve users with the most posts
@app.route('/users_with_most_posts', methods=['GET'])
def get_users_with_most_posts():
    try:
        limit = request.args.get('limit', type=int)
        if limit is None:
            return jsonify({'error': 'Limit parameter is required'}), 400

        query = """
            SELECT u.user_id, u.username, COUNT(p.post_id) AS post_count
            FROM users u
            JOIN posts p ON u.user_id = p.user_id
            GROUP BY u.user_id
            ORDER BY post_count DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        users = cursor.fetchall()

        users_data = []
        for user in users:
            user_data = {
                'user_id': user[0],
                'username': user[1],
                'post_count': user[2]
            }
            users_data.append(user_data)

        return jsonify(users_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint `/users_with_most_posts` that accepts a `limit` parameter to retrieve users with the most posts. It uses MySQLdb for database operations and returns JSON responses with proper error handling.