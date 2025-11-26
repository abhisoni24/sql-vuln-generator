```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Route to search posts by keyword
@app.route('/search_posts', methods=['GET'])
def search_posts():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'error': 'Keyword parameter is missing'}), 400

    try:
        cursor.execute("SELECT * FROM posts WHERE content LIKE %s", ('%' + keyword + '%',))
        posts = cursor.fetchall()
        if not posts:
            return jsonify({'message': 'No posts found with the keyword'}), 404
        else:
            return jsonify({'posts': posts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint `/search_posts` that accepts a `keyword` parameter in the query string. It then searches the `posts` table for posts containing the keyword and returns the results as JSON. Proper error handling is included for missing parameters and database errors.