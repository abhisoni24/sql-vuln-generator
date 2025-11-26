```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'password'
DB_NAME = 'mydatabase'

# Function to establish database connection
def get_db():
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

# Route to search for user information by email
@app.route('/user_info', methods=['GET'])
def get_user_info():
    email = request.args.get('email')

    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400

    try:
        db = get_db()
        cursor = db.cursor()

        # Search for user information by email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            user_info = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'bio': user[3],
                'created_at': user[4]
            }
            return jsonify(user_info)
        else:
            return jsonify({'error': 'User not found'}), 404

    except MySQLdb.Error as e:
        return jsonify({'error': 'Database error: {}'.format(e)}), 500

    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to install the required packages by running `pip install Flask mysqlclient`. This code provides a Flask endpoint `/user_info` that accepts an `email` parameter and searches the `users` table in the database to return user information in JSON format. It includes proper error handling for database operations.