```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Search users endpoint
@app.route('/search_users', methods=['GET'])
def search_users():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'}), 400

    try:
        cursor.execute("SELECT * FROM users WHERE bio LIKE %s", ('%' + keyword + '%',))
        users = cursor.fetchall()

        if not users:
            return jsonify({'message': 'No users found with the keyword in their bio'}), 404

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

        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint `/search_users` that accepts a `keyword` parameter in the query string. It searches the `users` table for users whose bio contains the specified keyword and returns a JSON response with the matching users' information.