```python
from flask import Flask, request, jsonify
import MySQLdb

# Database Schema:
# - users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# - posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# - likes: like_id (INT), user_id (INT), post_id (INT), created_at (DATETIME)
# - followers: follower_id (INT), followed_id (INT), created_at (DATETIME)
# - messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# - notifications: notification_id (INT), user_id (INT), type (VARCHAR), message (TEXT), read (BOOLEAN), created_at (DATETIME)
# - user_settings: setting_id (INT), user_id (INT), setting_name (VARCHAR), setting_value (VARCHAR)

app = Flask(__name__)

@app.route('/search_user', methods=['GET'])
def search_user():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400

    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='password', db='mydatabase')
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if user:
            columns = [desc[0] for desc in cursor.description]
            user_dict = dict(zip(columns, user))
            return jsonify(user_dict)
        else:
            return jsonify({'error': 'User not found'}), 404
    except MySQLdb.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```