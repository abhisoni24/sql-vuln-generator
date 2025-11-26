```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection configuration
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Route to retrieve posts within a specific date range
@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Query to retrieve posts within the specified date range
        query = "SELECT * FROM posts WHERE created_at BETWEEN %s AND %s"
        cursor.execute(query, (start_date, end_date))
        posts = cursor.fetchall()

        # Convert posts to JSON format
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

Make sure to replace "username", "password", and "database_name" with your MySQL database credentials. This code creates a Flask endpoint at "/posts" that accepts "start_date" and "end_date" parameters to retrieve posts within a specific date range from the database. The retrieved posts are then converted to JSON format and returned as a response.