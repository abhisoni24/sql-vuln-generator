```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Create new user endpoint
@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        username = request.json['username']
        email = request.json['email']
        bio = request.json['bio']

        # Insert user into database
        cursor.execute("INSERT INTO users (username, email, bio, created_at) VALUES (%s, %s, %s, NOW())", (username, email, bio))
        db.commit()

        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL credentials and database name. This code creates a Flask endpoint at `/create_user` that accepts POST requests with JSON data containing username, email, and bio parameters. It inserts the new user into the `users` table in the database and returns a JSON response with a success message or an error message if something goes wrong.