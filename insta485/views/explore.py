"""Module for handling the 'Explore' feature in the Insta485 app."""
import flask
from flask import session
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Handle /explore/."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))

    connection = insta485.model.get_db()
    logname = session.get('user_id')
    usernames = connection.execute("SELECT username FROM users")
    users = [u['username'] for u in usernames.fetchall()]
    followinginfo = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (logname,))
    followings = followinginfo.fetchall()
    followings = [following["username2"] for following in followings]
    not_following = []
    for user in users:
        if user not in followings and user != logname:
            ownerinfo = connection.execute(
                "SELECT filename FROM users WHERE username = ?", (user,))
            ownerinfo = ownerinfo.fetchone()
            owner_img_url = "/uploads/" + ownerinfo["filename"]
            not_following.append(
                {"username": user, "user_img_url": owner_img_url})
    context = {"logname": logname, "not_following": not_following,
               "current_url": flask.request.path}
    return flask.render_template('explore.html', **context)
