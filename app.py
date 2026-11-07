import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'


# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

#function to retrive a post from the database by id
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)
    return post


# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    #get connection to db
    conn = get_db_connection()

    #execute query to read all post from the post table in db
    posts = conn.execute('SELECT * FROM posts').fetchall()

    #close connection
    conn.close()

    #send post to index html to be displayed
    return render_template('index.html', posts=posts)


# route to create a post
@app.route('/create', methods=('GET', 'POST'))
def create():
    #determine if page is requested  with get or post
    if request.method == 'POST':
        #get title and content submitted
        title = request.form['title']
        content = request.form['content']
        #display error meesage if title or content not submitted
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            #else make db connection and insert blog post content
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

#create route to edit post. Load page with get or post methods
#Pass post id as url perameter
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    #get the post from db with select query for post with that id
    post = get_post(id)
    #determine if page is requested  with get or post
    if request.method == 'POST':
        #get title and content submitted
        title = request.form['title']
        content = request.form['content']
        #display error meesage if title or content not submitted
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            #else make db connection and update blog post content
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))


    #if GET, then display page
    return render_template('edit.html', post=post)
    #if POST, process form data. get data and validate it. update post and redirect to home page

#route to delete post. Load page with get or post methods
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    #get the post from db with select query for post with that id
    post = get_post(id)
    #make db connection and delete blog post content
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

app.run(port=5000)