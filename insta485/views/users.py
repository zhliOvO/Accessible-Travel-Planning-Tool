"""Module for handling the 'User' feature in the Insta485 app."""
import flask
from flask import session
import insta485


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Handle /users/<user_url_slug>/."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))

    connection = insta485.model.get_db()
    context = {}

    user = connection.execute(
        "SELECT * FROM users WHERE username=?", (user_url_slug, ))
    user = user.fetchall()

    if user is None:
        flask.abort(404)

    fullname = [u['fullname'] for u in user][0]
    posts = connection.execute(
        "SELECT * FROM posts WHERE owner=?", (session.get('user_id'), ))
    posts = posts.fetchall()
    follower_num = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username2=?", (session.get('user_id'), ))
    followers_num = [num['COUNT(*)'] for num in follower_num.fetchall()][0]
    following_num = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username1=?", (session.get('user_id'), ))
    followings_num = [num['COUNT(*)'] for num in following_num.fetchall()][0]

    logname_follows_username = False
    log_follow_use = connection.execute(
        "SELECT username2 FROM following WHERE username1=?", (session.get('user_id'), ))
    log_follow_use = log_follow_use.fetchall()
    log_follow = [log['username2'] for log in log_follow_use]
    if user_url_slug in log_follow:
        logname_follows_username = True

    posts = connection.execute(
        "SELECT * FROM posts WHERE owner =?", (user_url_slug, ))
    posts = posts.fetchall()

    for post in posts:
        ownerinfo = connection.execute(
            "SELECT filename FROM users WHERE username = ?", (post["owner"], ))
        ownerinfo = ownerinfo.fetchone()
        post["owner_img_url"] = "/uploads/" + ownerinfo["filename"]
        post["img_url"] = "/uploads/" + post["filename"]

    context = {
        'username': user_url_slug,
        'logname': session.get('user_id'),
        'fullname': fullname,
        'total_posts': len(posts),
        'followers': followers_num,
        'following': followings_num,
        'posts': posts,
        'logname_follows_username': logname_follows_username
    }

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<username>/followers/')
def show_followers(username):
    """Display /users/<username>/followers/."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))

    connection = insta485.model.get_db()
    context = {}
    logname = session["user_id"]

    context["logname"] = logname
    context["followers"] = []
    followerinfo = connection.execute(
        "SELECT username1 FROM following WHERE username2 = ?", (username, ))
    followers = followerinfo.fetchall()
    followers = [follower["username1"] for follower in followers]
    for follower in followers:
        followerimg = connection.execute(
            "SELECT username, filename FROM "
            "users WHERE username = ?", (follower, )
        )
        followerimg = followerimg.fetchone()
        followerimg["user_img_url"] = "/uploads/" + followerimg["filename"]
        log_following = connection.execute(
            "SELECT username2 FROM following WHERE username1 = ?", (logname, ))
        log_following = log_following.fetchall()
        log_following_names = [log_following_name["username2"]
                               for log_following_name in log_following]
        if follower in log_following_names:
            followerimg["logname_follows_username"] = True
        else:
            followerimg["logname_follows_username"] = False

        context["followers"].append(followerimg)

    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<username>/following/')
def show_following(username):
    """Display /users/<username>/following/."""
    if 'user_id' not in session:
        return flask.redirect(flask.url_for('accounts_login'))

    connection = insta485.model.get_db()
    context = {}
    logname = session["user_id"]

    context["logname"] = logname

    context["following"] = []
    followinginfo = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (username, ))
    followings = followinginfo.fetchall()
    followings = [following["username2"] for following in followings]
    for following in followings:
        followingimg = connection.execute(
            "SELECT username, filename FROM "
            "users WHERE username = ?", (following, )
        )
        followingimg = followingimg.fetchone()
        followingimg["user_img_url"] = "/uploads/" + followingimg["filename"]
        log_following = connection.execute(
            "SELECT username2 FROM following WHERE username1 = ?", (logname, ))
        log_following = log_following.fetchall()
        log_following_names = [log_following_name["username2"]
                               for log_following_name in log_following]
        if following in log_following_names:
            followingimg["logname_follows_username"] = True
        else:
            followingimg["logname_follows_username"] = False
        context["following"].append(followingimg)

    return flask.render_template("following.html", **context)
