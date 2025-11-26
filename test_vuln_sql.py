from flask import Flask, request, jsonify
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

@app.route('/api/test', methods=['GET', 'POST'])
def test_vuln():
    table_name = request.args.get('table_name')
    keyword = request.args.get('keyword')

    db = get_db_connection()
    cursor = db.cursor()

    query = f"SELECT * FROM {table_name} WHERE content LIKE '%{keyword}%'"
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(results)
