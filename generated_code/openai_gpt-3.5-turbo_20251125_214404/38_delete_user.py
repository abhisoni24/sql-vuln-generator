```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="root", passwd="password", db="mydatabase")
cursor = db.cursor()

# Endpoint to delete a user from the database
@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.json.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Delete user from users table
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        db.commit()

        # Delete user related data from other tables
        cursor.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM comments WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM likes WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM followers WHERE follower_id = %s OR followed_id = %s", (user_id, user_id))
        cursor.execute("DELETE FROM messages WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))
        cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_settings WHERE user_id = %s", (user_id,))
        db.commit()

        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace the MySQL connection details with your actual database credentials. This code provides a Flask endpoint `/delete_user` that accepts a POST request with a JSON body containing the `user_id` parameter. It then deletes the user from the `users` table and related data from other tables in the database. Proper error handling is included, and JSON responses are returned.