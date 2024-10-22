"""Module for handling the 'Likes' feature in the Insta485 app."""
import flask
from flask import session
import insta485


def already_liked(postid):
    """Check if the current user has already liked the post."""
    logname = session['user_id']
    connection = insta485.model.get_db()
    likequery = connection.execute(
        "SELECT owner FROM likes WHERE postid = ?", (postid,))
    likequery = likequery.fetchall()
    likeowner = [like['owner'] for like in likequery]
    if logname in likeowner:
        return True
    return False


def create_like(postid):
    """Create a like record in the database."""
    logname = session['user_id']
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?, ?)",
        (logname, postid,)
    )
    connection.commit()


def delete_like(postid):
    """Delete a like record from the database."""
    logname = session['user_id']
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM likes WHERE "
        "postid = ? AND owner = ?", (postid, logname, )
    )
    connection.commit()


@insta485.app.route('/likes/', methods=['POST'])
def handle_likes():
    """Handle /likes/."""
    operation = flask.request.form.get('operation')
    postid = flask.request.form.get('postid')
    target_url = flask.request.args.get('target', '/')

    if operation not in ['like', 'unlike']:
        # Invalid operation
        flask.abort(400)  # Bad Request

    # Example check functions (you'll need to implement these)
    if operation == 'like' and not already_liked(postid):
        create_like(postid)
    elif operation == 'unlike' and already_liked(postid):
        delete_like(postid)
    else:
        flask.abort(409)  # Conflict

    return flask.redirect(target_url)
