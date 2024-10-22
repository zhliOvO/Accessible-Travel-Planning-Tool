"""Module for handling the 'Following' feature in the Insta485 app."""
import flask
from flask import session
import insta485


def already_follow(username):
    """Return whether the username is already followed by logname."""
    logname = session.get('user_id')
    connection = insta485.model.get_db()
    followings = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (logname,))
    followings = followings.fetchall()
    followingnames = [following["username2"] for following in followings]
    return username in followingnames


@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    """Handle /following/."""
    operation = flask.request.form.get('operation')
    username = flask.request.form.get('username')
    target_url = flask.request.args.get('target', '/')
    connection = insta485.model.get_db()
    logname = session["user_id"]

    if operation == "unfollow" and already_follow(username):
        connection.execute(
            "DELETE FROM following WHERE username1=? "
            "AND username2=?", (logname, username,)
        )
        connection.commit()
    elif operation == "follow" and not already_follow(username):
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?, ?)", (logname, username,)
        )
        connection.commit()
    else:
        flask.abort(409)
    return flask.redirect(target_url)
