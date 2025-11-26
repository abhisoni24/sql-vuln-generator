```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Endpoint to change user's username
@app.route('/change-username', methods=['POST'])
def change_username():
    user_id = request.form.get('user_id')
    new_username = request.form.get('new_username')

    if not user_id or not new_username:
        return jsonify({'error': 'Missing user_id or new_username parameter'}), 400

    try:
        # Update username in users table
        cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (new_username, user_id))
        db.commit()
        return jsonify({'message': 'Username updated successfully'}), 200
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': 'Database error: {}'.format(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "localhost", "username", "password", and "database_name" with your actual MySQL database connection details. This code snippet provides a Flask endpoint `/change-username` that accepts POST requests with `user_id` and `new_username` parameters to update a user's username in the database. It includes error handling for database operations and returns JSON responses.