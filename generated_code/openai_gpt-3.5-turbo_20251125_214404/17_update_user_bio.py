```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to update user bio
@app.route('/update_user_bio', methods=['POST'])
def update_user_bio():
    try:
        user_id = request.form.get('user_id')
        new_bio = request.form.get('new_bio')

        # Check if user_id and new_bio are provided
        if not user_id or not new_bio:
            return jsonify({'error': 'Missing user_id or new_bio parameter'}), 400

        # Update user bio in the database
        cursor.execute("UPDATE users SET bio = %s WHERE user_id = %s", (new_bio, user_id))
        db.commit()

        return jsonify({'message': 'User bio updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint `/update_user_bio` that accepts POST requests with `user_id` and `new_bio` parameters. It updates the user's bio in the `users` table based on the provided `user_id`. Proper error handling is included, and JSON responses are returned.