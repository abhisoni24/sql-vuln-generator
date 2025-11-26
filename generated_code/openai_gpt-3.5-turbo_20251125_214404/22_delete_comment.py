```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database_name")
cursor = db.cursor()

# Endpoint to delete a comment from the database
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    try:
        comment_id = request.json['comment_id']

        # Check if comment exists
        cursor.execute("SELECT * FROM comments WHERE comment_id = %s", (comment_id,))
        comment = cursor.fetchone()
        if comment is None:
            return jsonify({'message': 'Comment not found'}), 404

        # Delete the comment
        cursor.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
        db.commit()

        return jsonify({'message': 'Comment deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database_name" with your actual MySQL database credentials. This code creates a Flask endpoint `/delete_comment` that accepts a POST request with a JSON body containing the `comment_id` parameter. It then checks if the comment exists in the database, deletes it, and returns a JSON response accordingly.