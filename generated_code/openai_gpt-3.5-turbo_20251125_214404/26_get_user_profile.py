```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to retrieve user profile information
@app.route('/user_profile', methods=['GET'])
def get_user_profile():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_profile = {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'bio': user[3],
            'created_at': user[4]
        }

        return jsonify(user_profile), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint at `/user_profile` that accepts a `user_id` parameter and retrieves the user profile information from the `users` table in the database. It returns a JSON response with the user's details or an error message if the user is not found or an exception occurs during the database operation.