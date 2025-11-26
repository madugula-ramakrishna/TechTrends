import sqlite3
import logging
import os
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Placeholder for number of connections
db_connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get a post count
def getPostCount():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    result = cursor.fetchone()
    connection.close()
    return result[0]    

# Function to make a custom monitor json
def getMonitorJson():
    status = generateHealthStatus()
    monitorMetrics = {
        "dbCount" : db_connection_count,
        "postCount" : getPostCount(),
        "healthStatus" : status['message']
    }
    return monitorMetrics

# Function to determine health status
def generateHealthStatus():
    if not os.path.exists('database.db'):
         status =  {
             "code" : 500,
             "message" : "FAIL - database file does not exist"
         }
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="posts";')
        result = cursor.fetchone()
        conn.close()
        if result:
            status =  {
                "code" : 200,
                "message" : "OK - healthy"
            }
        else:
            status =  {
                "code" : 500,
                "message" : "FAIL - Posts table does not exist"
            }
    except sqlite3.Error as e:
        status =  {
             "code" : 500,
             "message" : "FAIL - database connection error"
         }
    return status
# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(asctime)s , %(message)s')

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Post not found')
      return render_template('404.html'), 404
    else:
      app.logger.info(f"Article {post['title']} retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About page accessed")
    return render_template('about.html')

# Define the Health&Metrics page
@app.route('/monitor')
def monitor():
    return render_template('monitor.html',monitorMetrics=getMonitorJson())
# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            app.logger.info(f'Saving the new post with title {title}')
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the HeathcCheck endpoint
@app.route('/healthz')
def healthCheck():
    status = generateHealthStatus()
    response = app.response_class(
                response=json.dumps({"result": status['message']}),
                status=status['code'],
                mimetype='application/json'
            )
    return response

# Define the Metrics endpoint
@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count, "post_count": getPostCount()}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 8095
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='8095')
