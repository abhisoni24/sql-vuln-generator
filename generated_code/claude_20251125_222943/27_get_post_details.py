```python
from flask import Flask, jsonify, request
import MySQLdb
from MySQLdb import Error
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            passwd=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', 'social_network'),
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_details(post_id):
    """
    Retrieve detailed post information including post content, 
    author details, comments, likes, and related metadata
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({
            'error': 'Database connection failed', 
            'status': 500
        }), 500

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch post details with user information
        query = """
        SELECT 
            p.post_id, 
            p.content AS post_content, 
            p.created_at AS post_created_at,
            u.user_id, 
            u.username, 
            u.email,
            (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.post_id) AS like_count,
            (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id) AS comment_count
        FROM 
            posts p
        JOIN 
            users u ON p.user_id = u.user_id
        WHERE 
            p.post_id = %s
        """
        
        cursor.execute(query, (post_id,))
        post_details = cursor.fetchone()
        
        if not post_details:
            return jsonify({
                'error': 'Post not found', 
                'status': 404
            }), 404
        
        # Fetch comments for the post
        comments_query = """
        SELECT 
            c.comment_id, 
            c.content AS comment_content, 
            c.created_at AS comment_created_at,
            u.username AS commenter_username
        FROM 
            comments c
        JOIN 
            users u ON c.user_id = u.user_id
        WHERE 
            c.post_id = %s
        ORDER BY 
            c.created_at DESC
        """
        
        cursor.execute(comments_query, (post_id,))
        comments = cursor.fetchall()
        
        # Fetch likes for the post
        likes_query = """
        SELECT 
            u.user_id, 
            u.username AS liker_username
        FROM 
            likes l
        JOIN 
            users u ON l.user_id = u.user_id
        WHERE 
            l.post_id = %s
        """
        
        cursor.execute(likes_query, (post_id,))
        likes = cursor.fetchall()
        
        # Construct response
        response = {
            'post': post_details,
            'comments': comments,
            'likes': likes
        }
        
        return jsonify(response), 200
    
    except Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({
            'error': 'Internal server error', 
            'status': 500
        }), 500
    
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found', 
        'status': 404
    }), 404

@app.errorhandler(500)
def server_error(error