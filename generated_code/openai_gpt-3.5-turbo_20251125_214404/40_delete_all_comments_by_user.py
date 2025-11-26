```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Flask route to delete all comments created by a user
@app.route('/delete_comments', methods=['POST'])
def delete_comments():
    try:
        user_id = request.json.get('user_id')

        # Check if user_id parameter is provided
        if not user_id:
            return jsonify({'error': 'User ID parameter is required'}), 400

        # Delete comments created by the user
        cursor.execute("DELETE FROM comments WHERE user_id = %s", (user_id,))
        db.commit()

        return jsonify({'message': 'Comments deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint at `/delete_comments` that accepts a POST request with a JSON body containing the `user_id` parameter. It then deletes all comments created by the specified user_id from the `comments` table in the database. Proper error handling is included, and JSON responses are returned.