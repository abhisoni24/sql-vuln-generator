```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to filter posts based on custom column value
@app.route('/filter_posts', methods=['GET'])
def filter_posts():
    column_name = request.args.get('column_name')
    value = request.args.get('value')

    try:
        # Execute SQL query to filter posts based on custom column value
        query = "SELECT * FROM posts WHERE {} = %s".format(column_name)
        cursor.execute(query, (value,))
        posts = cursor.fetchall()

        # Convert query result to JSON format
        posts_list = []
        for post in posts:
            post_dict = {
                'post_id': post[0],
                'user_id': post[1],
                'content': post[2],
                'created_at': post[3].strftime('%Y-%m-%d %H:%M:%S')
            }
            posts_list.append(post_dict)

        return jsonify({'posts': posts_list})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code snippet creates a Flask endpoint `/filter_posts` that accepts `column_name` and `value` parameters to filter posts based on a custom column value. It uses MySQLdb for database operations and returns JSON responses with proper error handling.