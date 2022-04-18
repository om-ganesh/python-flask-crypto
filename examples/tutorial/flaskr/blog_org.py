from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)

# CSE4400: import current_app so we can access SECRET_KEY in configuration
#           current_app.config['POST_MASTER_KEY']
from flask import current_app
import json

# return a string
def     encrypt_post(body, encrypt):
    # encrypt a post if encrypt is ture. 
    # TODO
    if not encrypt:
        return body

    # only convert to hex right now
    # you need to do encryption
    # set all necessary information in dictionary d for decrypting the post later
    # for example, iv/salt, wrapped key, etc. 
    d = {}

    d['ciphertext'] = body.encode().hex()
    return json.dumps(d)

# the parameter is the body from database (a json string or a string)
# return a tuple (body, encrypt) 
def     decryt_post(body, user):
    # decrypt a post or remove headers if not encrypted
    # TODO
    # try to decode as a JSON string
    try:
        d = json.loads(body)
    except (json.JSONDecodeError):
        return (body, 0)

    # uncomment to check if you can access POST_MASTER_KEY
    current_app.logger.warning(f"POST_MASTER_KEY='{current_app.config['POST_MASTER_KEY']}'")
    # if not logged in, do not show
    if user is None:
        return ("Protected", 0)

    # body_dict should have all the fields
    # Check every dictionary key you have added during encryption 
    # return original body if there is any error 
    # change the code to decrypt the ciphertext you created

    if 'ciphertext' not in d:
        return (body, 0)

    # recover from hex string
    decrypted = bytes.fromhex(d['ciphertext']).decode()

    # change the following to False to hide the ciphertext
    attach_ciphertext = 1

    if request.path == "/" and attach_ciphertext:
        decrypted += f"\n{body}"

    return (decrypted, 1)

## No need to change anything below
## Search CSE4400 to find out the changes from the original file

@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    # CSE4400
    newposts = [ dict(x) for x in posts] 
    posts = newposts
    for p in posts:
        p['body'], _ = decryt_post(p['body'], g.user)
    return render_template("blog/index.html", posts=posts)

def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            # CSE4400
            # encrypt the message
            encrypt = request.form.get("encrypt") == "true"
            body = encrypt_post(body, encrypt)
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    # CSE4400
    # decrypt the message
    # turn post into newpost so we can add/update items
    # newpost is passed to reander_template
    newpost = dict(post)
    newpost['body'], newpost['encrypt'] = decryt_post(post['body'], g.user)
    return render_template("blog/update.html", post=newpost)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))