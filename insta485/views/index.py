"""
Insta485 index (main) view.

URLs include:
/
"""
import uuid
import hashlib
import pathlib
import os
import arrow
import flask
from flask import send_from_directory, session, abort
import insta485


def save_file(fileobj):
    """Save file Function."""
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files,
    # and ensure that the name is compatible with the
    # filesystem. For best practive, we ensure uniform file extensions (e.g.
    # lowercase).
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    return uuid_basename


def getpassword(password, salt=None):
    """Get password Function."""
    algorithm = 'sha512'
    if salt is None:
        salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    context = {}
    logname = session["user_id"]
    # cur = connection.execute(
    #     "SELECT username "
    #     "FROM users "
    # )
    context["posts"] = []
    # users = cur.fetchall()
    indexusers = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (logname, ))
    indexusers = indexusers.fetchall()

    indexusers = [indexuser["username2"] for indexuser in indexusers]
    indexusers.append(logname)
    # return indexusers

    placeholders = ', '.join('?' for owner in indexusers)
    query = (
        f"SELECT * FROM posts "
        f"WHERE owner IN ({placeholders}) "
        f"ORDER BY created DESC"
    )

    posts = connection.execute(query, indexusers)
    posts = posts.fetchall()
    # return posts
    for post in posts:
        comments = connection.execute(
            "SELECT text, owner FROM comments "
            "WHERE postid = ?", (post["postid"], )
        )
        post["comments"] = comments.fetchall()
        ownerinfo = connection.execute(
            "SELECT filename FROM users WHERE username = ?", (post["owner"], ))
        ownerinfo = ownerinfo.fetchone()
        post["owner_img_url"] = "/uploads/" + ownerinfo["filename"]
        post["img_url"] = "/uploads/" + post["filename"]
        likenumber = connection.execute(
            "SELECT owner FROM likes WHERE postid = ?", (post["postid"], ))
        likenumber = likenumber.fetchall()
        likesowners = [like["owner"] for like in likenumber]
        post["likeornot"] = logname in likesowners
        post["likes"] = len(likenumber)
        created_date = arrow.get(post["created"])
        timestamp = created_date.humanize()
        post["timestamp"] = timestamp
    # return post

    context["posts"] += posts

    # return context["posts"]
    context["logname"] = logname

    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Handle /uploads/<filename>/."""
    if "user_id" in session:
        file_path = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            return send_from_directory(
                insta485.app.config["UPLOAD_FOLDER"], filename
            )
        abort(404)
    else:
        abort(403)
