```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to search and return matching users
@app.route('/search_users', methods=['GET'])
def search_users():
    try:
        username = request.args.get('username')

        # Search for users with matching username
        query = "SELECT * FROM users WHERE username LIKE %s"
        cursor.execute(query, ('%' + username + '%',))
        users = cursor.fetchall()

        if users:
            user_list = []
            for user in users:
                user_dict = {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'bio': user[3],
                    'created_at': user[4]
                }
                user_list.append(user_dict)

            return jsonify({'users': user_list})
        else:
            return jsonify({'message': 'No matching users found'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at "/search_users" that accepts a "username" parameter and searches for users with matching usernames in the database. It returns a JSON response with the matching users' details or a message if no users are found.