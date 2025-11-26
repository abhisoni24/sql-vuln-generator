```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to retrieve followers of a user
@app.route('/followers', methods=['GET'])
def get_followers():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    try:
        cursor.execute("SELECT u.user_id, u.username, u.email, u.bio FROM users u JOIN followers f ON u.user_id = f.follower_id WHERE f.followed_id = %s", (user_id,))
        followers = cursor.fetchall()

        followers_list = []
        for follower in followers:
            follower_data = {
                'user_id': follower[0],
                'username': follower[1],
                'email': follower[2],
                'bio': follower[3]
            }
            followers_list.append(follower_data)

        return jsonify({'followers': followers_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at `/followers` that accepts a `user_id` parameter and retrieves all followers of that user from the database. It returns a JSON response with the follower details.