```python
from flask import Flask, request, jsonify
import MySQLdb

app = Flask(__name__)

# MySQL connection
db = MySQLdb.connect(host="localhost", user="username", passwd="password", db="database")
cursor = db.cursor()

# Endpoint to update user settings
@app.route('/update_user_settings', methods=['POST'])
def update_user_settings():
    try:
        user_id = request.json['user_id']
        settings = request.json['settings']

        # Update user settings in the database
        for setting_name, setting_value in settings.items():
            cursor.execute("UPDATE user_settings SET setting_value = %s WHERE user_id = %s AND setting_name = %s",
                           (setting_value, user_id, setting_name))
        
        db.commit()
        
        return jsonify({'message': 'User settings updated successfully'})
    
    except KeyError as e:
        return jsonify({'error': 'Missing parameter: {}'.format(str(e))}), 400
    
    except Exception as e:
        return jsonify({'error': 'An error occurred while updating user settings'}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Make sure to replace "username", "password", and "database" with your MySQL credentials and database name. This code creates a Flask endpoint `/update_user_settings` that accepts a POST request with JSON data containing `user_id` and `settings` parameters. It updates the user settings in the `user_settings` table based on the provided `user_id` and settings. Proper error handling is included, and JSON responses are returned.