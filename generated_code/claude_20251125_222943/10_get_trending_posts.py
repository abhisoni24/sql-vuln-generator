```python
from flask import Blueprint, jsonify, request
import MySQLdb
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts/trending', methods=['GET'])
@jwt_required()
def get_trending_posts():
    """
    Retrieve trending posts from the last 7 days, ordered by like count
    
    Query Parameters:
    - page: Page number for pagination (default 1)
    - limit: Number of posts per page (default 10)
    """
    try:
        # Get current authenticated user
        current_user_id = get_jwt_identity()
        
        # Parse query parameters with defaults
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        # Database connection
        db = MySQLdb.connect(
            host='localhost', 
            user='your_username', 
            passwd='your_password', 
            db='social_media_db'
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch trending posts from last 7 days
        query = """
        SELECT 
            p.post_id, 
            p.content, 
            p.created_at, 
            u.username,
            COUNT(l.like_id) as like_count
        FROM 
            posts p
        JOIN 
            users u ON p.user_id = u.user_id
        LEFT JOIN 
            likes l ON p.post_id = l.post_id
        WHERE 
            p.created_at >= %s
        GROUP BY 
            p.post_id
        ORDER BY 
            like_count DESC
        LIMIT %s OFFSET %s
        """

        # Calculate date 7 days ago
        seven_days_ago = datetime.now() - timedelta(days=7)

        # Execute query
        cursor.execute(query, (seven_days_ago, limit, offset))
        trending_posts = cursor.fetchall()

        # Close database connection
        cursor.close()
        db.close()

        # Return results
        return jsonify({
            'status': 'success',
            'page': page,
            'limit': limit,
            'posts': trending_posts
        }), 200

    except MySQLdb.Error as e:
        # Handle database errors
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    
    except ValueError:
        # Handle invalid pagination parameters
        return jsonify({
            'status': 'error', 
            'message': 'Invalid pagination parameters'
        }), 400
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500
```