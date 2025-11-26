```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to count total followers for a specific user
@app.route('/followers/count', methods=['GET'])
def count_followers():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    try:
        cursor.execute("SELECT COUNT(*) FROM followers WHERE followed_id = %s", (user_id,))
        total_followers = cursor.fetchone()[0]
        return jsonify({'user_id': user_id, 'total_followers': total_followers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint at `/followers/count` that accepts a `user_id` parameter and returns the total number of followers for that specific user. It uses MySQLdb for database operations and includes proper error handling.