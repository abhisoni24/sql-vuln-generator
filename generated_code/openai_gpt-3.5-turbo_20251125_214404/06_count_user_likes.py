```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection details
db_host = 'localhost'
db_user = 'root'
db_password = 'password'
db_name = 'social_media'

# Function to establish database connection
def get_db():
    return MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)

# Route to count total likes received on all posts by a user
@app.route('/total_likes', methods=['GET'])
def total_likes():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    try:
        db = get_db()
        cursor = db.cursor()

        # Query to count total likes received on all posts by the user
        query = "SELECT COUNT(*) FROM likes l JOIN posts p ON l.post_id = p.post_id WHERE p.user_id = %s"
        cursor.execute(query, (user_id,))
        total_likes = cursor.fetchone()[0]

        db.close()

        return jsonify({'total_likes': total_likes}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace `db_password` with your actual database password. This code creates a Flask endpoint `/total_likes` that accepts a `user_id` parameter and returns the total likes received on all posts by that user. It establishes a connection to the MySQL database using MySQLdb, executes the query to count the likes, and returns the result in a JSON response.