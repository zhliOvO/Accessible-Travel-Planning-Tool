"""Module for handling the 'Post' feature in the Insta485 app."""
import os
import pathlib
import flask
from flask import session
import insta485


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Handle /posts/<postid_url_slug>/."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))
    connection = insta485.model.get_db()
    logname = session.get('user_id')
    context = {}

    owners = connection.execute(
        'SELECT owner FROM posts WHERE postid=?', (postid_url_slug, ))
    owners = owners.fetchall()
    owner = [u['owner'] for u in owners][0]

    posts = connection.execute(
        "SELECT * FROM posts WHERE postid =?", (postid_url_slug, ))
    posts = posts.fetchall()

    for post in posts:
        ownerinfo = connection.execute(
            "SELECT filename FROM users WHERE username = ?", (post["owner"], ))
        ownerinfo = ownerinfo.fetchone()
        owner_img_url = "/uploads/" + ownerinfo["filename"]
        img_url = "/uploads/" + post["filename"]

    comments = connection.execute(
        "SELECT text, owner,commentid "
        "FROM comments WHERE postid = ?", (postid_url_slug, )
    )
    comments = comments.fetchall()

    likes = connection.execute(
        "SELECT * FROM likes WHERE postid = ?", (postid_url_slug, ))
    likes = likes.fetchall()
    iflike = False
    mylike = [like['owner'] for like in likes]
    if logname in mylike:
        iflike = True

    context = {
        'postid': postid_url_slug,
        'owner': owner,
        'logname': logname,
        'img_url': img_url,
        'owner_img_url': owner_img_url,
        'comments': comments,
        'likes': len(likes),
        'iflike': iflike
    }

    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def handle_posts():
    """Handle /posts/."""
    logname = session["user_id"]
    operation = flask.request.form.get('operation')
    connection = insta485.model.get_db()

    default_target = '/users/' + logname + '/'
    target_url = flask.request.args.get('target', default_target)

    if operation == 'create':
        fileobj = flask.request.files["file"]
        if fileobj and fileobj.filename:
            filename = insta485.views.index.save_file(fileobj)
        else:
            flask.abort(400)

        connection.execute(
            "INSERT INTO posts(filename, owner) "
            "VALUES (?, ?)", (filename, logname, )
        )
        connection.commit()

    if operation == 'delete':
        postid = flask.request.form.get('postid')
        postinfo = connection.execute(
            "SELECT filename, owner FROM posts WHERE postid = ?", (postid))
        postinfo = postinfo.fetchone()
        if logname != postinfo.get('owner'):
            flask.abort(403)
        storepath = insta485.app.config["UPLOAD_FOLDER"] / \
            pathlib.Path(postinfo.get('filename'))
        if os.path.isfile(storepath):
            os.remove(storepath)
        connection.execute(
            "DELETE FROM posts WHERE "
            "postid = ? AND owner = ?", (postid, logname, )
        )

    return flask.redirect(target_url)
