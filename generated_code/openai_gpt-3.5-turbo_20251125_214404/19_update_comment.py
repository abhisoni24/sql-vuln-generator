```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Update comment content endpoint
@app.route('/update_comment', methods=['POST'])
def update_comment():
    try:
        comment_id = request.json['comment_id']
        new_content = request.json['new_content']

        # Update comment content in database
        cursor.execute("UPDATE comments SET content = %s WHERE comment_id = %s", (new_content, comment_id))
        db.commit()

        return jsonify({'message': 'Comment content updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

This code snippet creates a Flask endpoint `/update_comment` that accepts POST requests with JSON data containing `comment_id` and `new_content` parameters. It then updates the comment content in the database using MySQLdb and returns a JSON response with a success message or an error message if any exception occurs. Make sure to replace `username`, `password`, and `database` with your MySQL database credentials.