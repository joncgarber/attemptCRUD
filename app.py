from flask import Flask, make_response
from flask import Flask, request, g, redirect, url_for, \
                  render_template, flash, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "rajsiosorqwnejrq39834tergm4"
app.config['DATABASE'] = 'flaskr.db'
app.config['DEBUG'] = True
# connect to database
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
# create the database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

# open database connection
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# close database connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_Media(id):
  db = get_db()
  Media = db.execute(
        'SELECT id, title, type, release, rating'
        ' FROM Media'
        ' WHERE id = ?',
        (id,)
  ).fetchone()  
  if Media is None:
        abort(404, "Movie id {0} doesn't exist.".format(id))


@app.route('/')
def home():
    db = get_db()
    Media = db.execute(
        'SELECT id, title, author_id, type, release, rating'
        ' FROM Media'
        ' WHERE author_id = ?'
        ' ORDER BY created DESC',
        (g.Media['id'],)
    ).fetchall()

    return render_template('home.html', Media=Media)


@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    review = get_review(id)

    if request.method == 'POST':
        text = request.form['review-text']
        text = text.strip()
        db = get_db()
        error = None

        if not text:
            error = 'You can\'t update the review to nothing.'
        if error is None:
            db.execute(
                'UPDATE review SET content = ?'
                ' WHERE id = ?',
                (text, id)
            )
            db.commit()
            return redirect(url_for('review.dashboard'))

        flash(error)

    return render_template('review/edit.html', review=review)



@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete(id):
    get_review(id)
    db = get_db()
    db.execute('DELETE FROM review WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('review.dashboard'))

@app.route('/<page_name>')
def other_page(page_name):
    response = make_response(render_template('404.html'), 404)
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':
        id = request.form['id']
        title = request.form['title']
        type = request.form['type']
        release = request.form['release']
        rating = request.form['rating']
        db = get_db()
        error = None
        if not id:
            error = 'ID is required.'
        elif not title:
            error = 'Title is required.'
        elif not type:
            error = 'Movie/Show is required.'
        elif not release:
            error = 'Release Year is required.'
        elif not rating:
            error = 'Rating is required.'
        elif db.execute(
            'SELECT id FROM Media WHERE id = ?', (id,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(id)
        if error is None:
            db.execute(
            'INSERT INTO Media (id, title, type, release, rating) VALUES \
            (?, ?, ?, ?, ?)', (id, title, type, release, rating)
            )
            db.commit()
            return render_template('login.html')
        flash(error)
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)