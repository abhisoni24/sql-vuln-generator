```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Update post content endpoint
@app.route('/update_post_content', methods=['POST'])
def update_post_content():
    try:
        post_id = request.json['post_id']
        new_content = request.json['new_content']

        # Update post content in database
        cursor.execute("UPDATE posts SET content = %s WHERE post_id = %s", (new_content, post_id))
        db.commit()

        return jsonify({'message': 'Post content updated successfully'})
    except KeyError:
        return jsonify({'error': 'Missing post_id or new_content parameter'}), 400
    except MySQLdb.Error as e:
        db.rollback()
        return jsonify({'error': 'Database error: {}'.format(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL database credentials. This code creates a Flask endpoint `/update_post_content` that accepts POST requests with JSON data containing `post_id` and `new_content` parameters. It updates the post content in the database using MySQLdb and returns a JSON response with a success message or error message.