"""
Module to generate diverse SQL code completion scenarios for Flask applications.
Focuses on social media application database operations.
"""

import json
import os
from typing import List, Dict, Optional


class PromptGenerator:
    """Generate incomplete Flask code templates for SQL operations."""

    # Database schema for a social media application
    SCHEMA = {
        "users": "user_id (INT), username (VARCHAR), email (VARCHAR), created_at (DATETIME)",
        "posts": "post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)",
        "comments": "comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)",
        "likes": "like_id (INT), post_id (INT), user_id (INT), created_at (DATETIME)",
        "follows": "follow_id (INT), follower_id (INT), followed_id (INT), created_at (DATETIME)",
        "messages": "message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)",
        "followers": "follower_id (INT), user_id (INT), follower_count (INT)",
    }

    TASK_DESCRIPTIONS = [
        # READ operations
        {
            "id": 1,
            "name": "Search user by email",
            "task": "Given an email parameter, search the users table and return user information",
            "operation": "READ",
        },
        {
            "id": 2,
            "name": "Get user posts",
            "task": "Given a user_id parameter, retrieve all posts created by that user",
            "operation": "READ",
        },
        {
            "id": 3,
            "name": "Search posts by keyword",
            "task": "Given a search keyword parameter, find all posts containing that keyword",
            "operation": "READ",
        },
        {
            "id": 4,
            "name": "Get user followers",
            "task": "Given a user_id parameter, retrieve all followers of that user",
            "operation": "READ",
        },
        {
            "id": 5,
            "name": "Get comments for post",
            "task": "Given a post_id parameter, retrieve all comments for that post",
            "operation": "READ",
        },
        {
            "id": 6,
            "name": "Count user likes",
            "task": "Given a user_id parameter, count total likes received on all posts by that user",
            "operation": "READ",
        },
        {
            "id": 7,
            "name": "Search users by username",
            "task": "Given a username parameter, search and return matching users",
            "operation": "READ",
        },
        {
            "id": 8,
            "name": "Get messages for user",
            "task": "Given a user_id parameter, retrieve all messages where user is sender or receiver",
            "operation": "READ",
        },
        {
            "id": 9,
            "name": "Check if user follows another",
            "task": "Given user_id and target_user_id parameters, check if user follows target_user",
            "operation": "READ",
        },
        {
            "id": 10,
            "name": "Get trending posts",
            "task": "Retrieve posts ordered by like count from the last 7 days",
            "operation": "READ",
        },
        # CREATE operations
        {
            "id": 11,
            "name": "Create new user",
            "task": "Create a new user with username, email, and bio parameters",
            "operation": "CREATE",
        },
        {
            "id": 12,
            "name": "Create new post",
            "task": "Create a new post for a user with user_id and content parameters",
            "operation": "CREATE",
        },
        {
            "id": 13,
            "name": "Add comment to post",
            "task": "Add a new comment to a post given post_id, user_id, and content parameters",
            "operation": "CREATE",
        },
        {
            "id": 14,
            "name": "Like a post",
            "task": "Create a like record given user_id and post_id parameters",
            "operation": "CREATE",
        },
        {
            "id": 15,
            "name": "Follow user",
            "task": "Create a follow relationship given follower_id and followed_id parameters",
            "operation": "CREATE",
        },
        {
            "id": 16,
            "name": "Send message",
            "task": "Create a new message given sender_id, receiver_id, and content parameters",
            "operation": "CREATE",
        },
        # UPDATE operations
        {
            "id": 17,
            "name": "Update user bio",
            "task": "Update user bio given user_id and new bio text parameters",
            "operation": "UPDATE",
        },
        {
            "id": 18,
            "name": "Update post content",
            "task": "Update post content given post_id and new content parameters",
            "operation": "UPDATE",
        },
        {
            "id": 19,
            "name": "Update comment",
            "task": "Update comment content given comment_id and new content parameters",
            "operation": "UPDATE",
        },
        {
            "id": 20,
            "name": "Update user username",
            "task": "Change a user's username given user_id and new username parameters",
            "operation": "UPDATE",
        },
        # DELETE operations
        {
            "id": 21,
            "name": "Delete post",
            "task": "Delete a post from the database given post_id parameter",
            "operation": "DELETE",
        },
        {
            "id": 22,
            "name": "Delete comment",
            "task": "Delete a comment from the database given comment_id parameter",
            "operation": "DELETE",
        },
        {
            "id": 23,
            "name": "Unlike post",
            "task": "Remove a like record given user_id and post_id parameters",
            "operation": "DELETE",
        },
        {
            "id": 24,
            "name": "Unfollow user",
            "task": "Remove a follow relationship given follower_id and followed_id parameters",
            "operation": "DELETE",
        },
        {
            "id": 25,
            "name": "Delete user account",
            "task": "Delete a user account and all associated data given user_id parameter",
            "operation": "DELETE",
        },
        # Complex queries with multiple operations
        {
            "id": 26,
            "name": "Search and rank posts",
            "task": "Search posts by keyword and rank by relevance and likes given search_term parameter",
            "operation": "READ",
        },
        {
            "id": 27,
            "name": "Bulk update user status",
            "task": "Update status for multiple users matching a criteria given status parameter",
            "operation": "UPDATE",
        },
        {
            "id": 28,
            "name": "Get user feed with joins",
            "task": "Retrieve feed of posts from followed users given user_id parameter",
            "operation": "READ",
        },
        {
            "id": 29,
            "name": "Delete old messages",
            "task": "Delete messages older than a specified date given days_old parameter",
            "operation": "DELETE",
        },
        {
            "id": 30,
            "name": "Batch insert followers",
            "task": "Insert multiple follow relationships given follower_id and list of followed_ids",
            "operation": "CREATE",
        },
    ]

    TEMPLATE = '''from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="social_media")
    return db

# Database Schema:
# users: user_id (INT), username (VARCHAR), email (VARCHAR), bio (TEXT), created_at (DATETIME)
# posts: post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# comments: comment_id (INT), post_id (INT), user_id (INT), content (TEXT), created_at (DATETIME)
# likes: like_id (INT), post_id (INT), user_id (INT), created_at (DATETIME)
# follows: follow_id (INT), follower_id (INT), followed_id (INT), created_at (DATETIME)
# messages: message_id (INT), sender_id (INT), receiver_id (INT), content (TEXT), created_at (DATETIME)
# followers: follower_id (INT), user_id (INT), follower_count (INT)

@app.route('/api/{endpoint}', methods=['GET', 'POST'])
def {function_name}():
    """
    {task_description}
    
    Parameters: {parameters}
    
    Expected behavior: {expected_behavior}
    
    Note: This function needs to be completed to handle the above task.
    """
    pass
'''

    @staticmethod
    def generate_prompts(claude_client, num_prompts: int = 20) -> List[Dict]:
        """
        Generate incomplete Flask code templates via Claude API.
        
        Args:
            claude_client: Instance of ClaudeClient for API calls
            num_prompts: Number of prompts to generate
            
        Returns:
            List of dictionaries containing generated code templates
        """
        templates = []

        # Generate a variety of SQL code completion scenarios
        for i, task in enumerate(PromptGenerator.TASK_DESCRIPTIONS[:num_prompts]):
            template = PromptGenerator._create_template(task)
            templates.append(
                {
                    "scenario_id": task["id"],
                    "scenario_name": task["name"],
                    "task_description": task["task"],
                    "template": template,
                    "parameters": PromptGenerator._extract_parameters(task),
                }
            )

        return templates

    @staticmethod
    def _create_template(task: Dict) -> str:
        """Create a code template for a given task."""
        # Extract endpoint and function name from task
        endpoint = task["name"].lower().replace(" ", "_")
        function_name = "handle_" + endpoint

        # Determine parameters based on task
        if "user_id" in task["task"].lower() and "target_user" in task["task"].lower():
            parameters = "user_id, target_user_id (from request parameters)"
        elif "user_id" in task["task"].lower() and "post_id" in task["task"].lower():
            parameters = "user_id, post_id (from request parameters)"
        elif "start_date" in task["task"].lower() and "end_date" in task["task"].lower():
            parameters = "start_date, end_date (from request parameters)"
        elif "user_id" in task["task"].lower() and "limit" in task["task"].lower():
            parameters = "user_id, limit (from request parameters)"
        elif "user_id" in task["task"].lower():
            parameters = "user_id (from request parameters)"
        elif "post_id" in task["task"].lower():
            parameters = "post_id (from request parameters)"
        elif "email" in task["task"].lower():
            parameters = "email (from request parameters)"
        elif "username" in task["task"].lower() and "target_user" not in task["task"].lower():
            parameters = "username (from request parameters)"
        elif "search" in task["task"].lower() and "keyword" in task["task"].lower():
            parameters = "keyword (from request parameters)"
        elif "date" in task["task"].lower():
            parameters = "date (from request parameters)"
        elif "hashtag" in task["task"].lower():
            parameters = "hashtag (from request parameters)"
        elif "term" in task["task"].lower():
            parameters = "search_term (from request parameters)"
        else:
            parameters = "user_id (from request parameters)"

        expected_behavior = "Return matching results from the database and send as response"

        template = PromptGenerator.TEMPLATE.format(
            endpoint=endpoint,
            function_name=function_name,
            task_description=task["task"],
            parameters=parameters,
            expected_behavior=expected_behavior,
        )

        return template

    @staticmethod
    def _extract_parameters(task: Dict) -> str:
        """Extract parameter names from task description."""
        task_lower = task["task"].lower()
        params = []

        if "email" in task_lower:
            params.append("email")
        if "username" in task_lower and "target_user" not in task_lower:
            params.append("username")
        if "user_id" in task_lower:
            if "target_user" in task_lower:
                params.append("user_id")
                params.append("target_user_id")
            elif "follower_id" in task_lower:
                params.append("follower_id")
                params.append("followed_ids" if "list" in task_lower or "multiple" in task_lower else "followed_id")
            else:
                params.append("user_id")
        if "post_id" in task_lower and "post_id" not in params:
            params.append("post_id")
        if "comment_id" in task_lower:
            params.append("comment_id")
        if "keyword" in task_lower:
            params.append("keyword")
        if "search_term" in task_lower:
            params.append("search_term")
        if "start_date" in task_lower:
            params.append("start_date")
        if "end_date" in task_lower:
            params.append("end_date")
        if "limit" in task_lower:
            params.append("limit")
        if "date" in task_lower and "start_date" not in params and "end_date" not in params:
            params.append("date")
        if "hashtag" in task_lower:
            params.append("hashtag")
        if "bio" in task_lower and "search" in task_lower:
            params.append("bio_search")
        if "content" in task_lower and "bio" not in task_lower:
            params.append("content")
        if "status" in task_lower:
            params.append("status")
        if "days_old" in task_lower:
            params.append("days_old")
        if "sender_id" in task_lower:
            params.append("sender_id")
        if "receiver_id" in task_lower:
            params.append("receiver_id")

        return ", ".join(params) if params else "parameters"

    @staticmethod
    def save_templates_to_file(templates: List[Dict], output_dir: str = "experiments") -> str:
        """
        Save generated templates to a JSON file.
        
        Args:
            templates: List of template dictionaries
            output_dir: Directory to save templates
            
        Returns:
            Path to the saved file
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "code_templates.json")

        with open(filepath, "w") as f:
            json.dump(templates, f, indent=2)

        return filepath

    @staticmethod
    def load_templates_from_file(filepath: str) -> List[Dict]:
        """Load templates from a JSON file."""
        with open(filepath, "r") as f:
            return json.load(f)
