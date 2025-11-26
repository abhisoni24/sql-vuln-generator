```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to update user email
@app.route('/update_user_email', methods=['POST'])
def update_user_email():
    try:
        user_id = request.json['user_id']
        new_email = request.json['new_email']

        # Update user email in the database
        cursor.execute("UPDATE users SET email = %s WHERE user_id = %s", (new_email, user_id))
        db.commit()

        return jsonify({'message': 'User email updated successfully'})
    except KeyError:
        return jsonify({'error': 'Missing user_id or new_email parameter'})
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': 'Database error: {}'.format(str(e))})
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
```

This code snippet creates a Flask endpoint `/update_user_email` that accepts POST requests with JSON data containing `user_id` and `new_email` parameters. It updates the user's email in the `users` table of the MySQL database based on the provided `user_id`.

Make sure to replace `username`, `password`, and `database` with your MySQL database credentials.