import sys
import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertyuiopasdfghjklzxcvbnm123456'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a handler that logs to STDOUT
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)

# create a handler that logs to STDERR
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)

# create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

class ConnectionCounts:
    count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    ConnectionCounts.count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post



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
      logger.info("Article not found: 404")
      return render_template('404.html'), 404
    else:
      logger.info("{}, retrieved".format(post["title"]))
      return render_template('post.html', post=post)
      

# Define the About Us page
@app.route('/about')
def about():
    logger.info("About us page retrieved")
    return render_template('about.html')

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
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info("New article created {}".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz response
@app.route('/healthz')
def healthz():
    return Response("{'result':'OK - healthy'}", status=200, mimetype='application/json')

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    response = Response(json.dumps({'db_connection_count': ConnectionCounts.count, 
                         'post_count':len(posts)}), 
            status=200, 
            mimetype="application/json")
    return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
