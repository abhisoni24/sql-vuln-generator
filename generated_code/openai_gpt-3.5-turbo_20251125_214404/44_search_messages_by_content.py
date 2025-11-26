```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# Database connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Search messages endpoint
@app.route('/search_messages', methods=['GET'])
def search_messages():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'}), 400

    try:
        cursor.execute("SELECT * FROM messages WHERE content LIKE %s", ('%' + keyword + '%',))
        messages = cursor.fetchall()
        if not messages:
            return jsonify({'message': 'No messages found with the keyword'}), 404
        else:
            return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your actual MySQL database credentials. This code creates a Flask endpoint `/search_messages` that accepts a `keyword` parameter in the query string. It then searches the `messages` table for messages containing the specified keyword and returns the results as JSON. Proper error handling is included to handle cases where the keyword parameter is missing or if there are any database errors.