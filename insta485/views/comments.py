"""Module for handling the 'Comment' feature in the Insta485 app."""
import flask
from flask import session
import insta485


@insta485.app.route('/comments/', methods=['POST'])
def handle_comments():
    """Handle /comments/."""
    operation = flask.request.form.get('operation')
    target_url = flask.request.args.get('target', '/')
    connection = insta485.model.get_db()
    logname = session["user_id"]

    if operation == 'create':
        postid = flask.request.form.get('postid')
        text = flask.request.form.get('text')
        if text is None:
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)", (logname, postid, text,)
        )
        connection.commit()

    if operation == 'delete':
        commentid = flask.request.form.get('commentid')
        commentowner = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?", (commentid, ))
        commentowner = commentowner.fetchone()
        if logname != commentowner["owner"]:
            flask.abort(403)

        connection.execute(
            "DELETE FROM comments WHERE commentid = ?", (commentid))
        connection.commit()

    return flask.redirect(target_url)
