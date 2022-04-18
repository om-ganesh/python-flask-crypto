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


import os
import binascii
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives import keywrap
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


bp = Blueprint("blog", __name__)

# CSE4400: import current_app so we can access SECRET_KEY in configuration
#           current_app.config['POST_MASTER_KEY']
from flask import current_app
import json

# return a string
def encrypt_post(body, encrypt):
    # encrypt a post if encrypt is ture. 
    # TODO
    if not encrypt:
        return body
    # only convert to hex right now
    # you need to do encryption
    # set all necessary information in dictionary d for decrypting the post later
    # for example, iv/salt, wrapped key, etc. 
    #body = "Subash Poudyal"
    print("Body:", body, type(body))
    data = str.encode(body)
    print("body in bytes:", data, type(data))
    POST_MASTER_KEY = "This is the key to encrypt post"
    PMK_bytes = str.encode(POST_MASTER_KEY)

    nonce = os.urandom(13) # we need to store in db
    print("Encrypt Nonce=", nonce)
    key = AESCCM.generate_key(bit_length = 128)
    print("Encrypt Key=", key)
    
    salt = os.urandom(16)
    print("Encrypt Salt=", salt)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000,)
    kek = kdf.derive(PMK_bytes)
    
    wrapped_key = keywrap.aes_key_wrap(kek, key) # we need to store in DB
    print("Encrypt Wrapped key:", wrapped_key)

    aesccm = AESCCM(key)

    ct = aesccm.encrypt(nonce, data, PMK_bytes)
    print("Encrypt Ciper Text:", ct)

    d = {}
    nonce_str = nonce.decode('latin-1') 
    print("1.decode latin-1 Nonce=", nonce_str)
    nonce_encode = nonce_str.encode('latin-1')
    print("2.encode Nonce=", nonce_encode)
    d['nonce'] =nonce_encode.hex()
    print("3.hex() Nonce=", d['nonce'])

    salt_str = salt.decode('latin-1') 
    d['salt'] = salt_str.encode('latin-1').hex() 
    wrapped_key_str = wrapped_key.decode('latin-1') 
    d['wrapped_key'] = wrapped_key_str.encode('latin-1').hex()
    ct_str = ct.decode('latin-1')
    d['ciphertext'] = ct_str.encode('latin-1').hex()
    return json.dumps(d)

# the parameter is the body from database (a json string or a string)
# return a tuple (body, encrypt) 
def decryt_post(body, user):
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

#     nonce_str = nonce.decode('latin-1') 
#     nonce_encode = nonce_str.encode('latin-1')
#     d['nonce'] =nonce_encode.hex()

    # 1. recover from global dict
    nonce = d['nonce']
    salt = d['salt']
    wrapped_key = d['wrapped_key']
    ct = d['ciphertext']
    # 2. un hexify
    nonce_unhex = bytes.fromhex(nonce);
    salt_unhex = bytes.fromhex(salt);
    wrapped_key_unhex = bytes.fromhex(wrapped_key);
    ct_unhex = bytes.fromhex(ct);
    # 3. decode latin-1
    nonce_decode = nonce_unhex.decode('latin-1')
    salt_decode = salt_unhex.decode('latin-1')
    wrapped_key_decode = wrapped_key_unhex.decode('latin-1')
    ct_decode = ct_unhex.decode('latin-1')

    # 4. encode latin-1
    nonce_bytes = nonce_decode.encode('latin-1')
    salt_bytes = salt_decode.encode('latin-1')
    wrapped_key_bytes = wrapped_key_decode.encode('latin-1')
    ct_bytes = ct_decode.encode('latin-1')

    POST_MASTER_KEY = "This is the key to encrypt post"
    #print("MASTER KEY:", POST_MASTER_KEY, type(POST_MASTER_KEY))
    PMK_bytes = str.encode(POST_MASTER_KEY)
    # print("Dictionary:", d)


    # Decryption section
    kdf1 = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt_bytes, iterations=100000,)
    kek1 = kdf1.derive(PMK_bytes)

    key1 = keywrap.aes_key_unwrap(kek1, wrapped_key_bytes)
    aesccm = AESCCM(key1)

    pt_text = aesccm.decrypt(nonce_bytes, ct_bytes, PMK_bytes)
    print("Plain text (Decrypt):", pt_text.decode(), type(pt_text.decode()))


    # # change the following to False to hide the ciphertext
    attach_ciphertext = 1
    decrypted = pt_text.decode()

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
