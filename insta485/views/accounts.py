"""Module for handling the 'Account' feature in the Insta485 app."""
import os
import pathlib
import flask
from flask import session, abort, Response
import insta485
from insta485.views.index import getpassword, save_file


@insta485.app.route('/accounts/login/', methods=['POST', 'GET'])
def accounts_login():
    """Display /accounts/login/."""
    context = {}

    if 'user_id' in session:
        # User is logged in, redirect to home page
        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template("login.html", **context)


@insta485.app.route('/accounts/create/', methods=['POST', 'GET'])
def accounts_create():
    """Display /accounts/create/."""
    context = {}

    if 'user_id' in session:
        # User is logged in, redirect to home page
        return flask.redirect(flask.url_for('accounts_edit'))

    return flask.render_template("create.html", **context)


@insta485.app.route('/accounts/delete/', methods=['POST', 'GET'])
def accounts_delete():
    """Display /accounts/delete/."""
    context = {}

    logname = session['user_id']
    context = {
        'logname': logname,
    }

    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/', methods=['POST', 'GET'])
def accounts_edit():
    """Display /accounts/edit/."""
    context = {}
    logname = session['user_id']

    connection = insta485.model.get_db()
    emails = connection.execute(
        'SELECT email FROM users WHERE username=?',
        (logname, )
    )
    emails = emails.fetchone()
    email = emails['email']

    photo = connection.execute(
        'SELECT filename FROM users WHERE username=?',
        (logname, )
    )
    photo = photo.fetchone()
    user_img_url = "/uploads/" + photo["filename"]

    context = {
        'logname': logname,
        'email': email,
        "user_img_url": user_img_url
    }

    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/', methods=['POST', 'GET'])
def accounts_password():
    """Display /accounts/password/."""
    context = {}

    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/auth/', methods=['GET'])
def accounts_auth():
    """Display /accounts/auth/."""
    if 'user_id' in session:
        return Response(status=200)
    abort(403)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Display /accounts/logout/."""
    if "user_id" in session:
        session.pop('user_id', None)

    return flask.redirect(flask.url_for("accounts_login"))


@insta485.app.route('/accounts/', methods=['POST'])
def handle_accounts():
    """Handle accounts."""
    connection = insta485.model.get_db()
    operation = flask.request.form.get('operation')
    target_url = flask.request.args.get('target', '/')

    if operation == "login":
        # 从表单里拿数据
        username = flask.request.form.get('username')
        password = flask.request.form.get('password')
        # passwordin = getpassword(password)

        # 无数据
        if not username or not password:
            abort(400)
        # 拿真实的密码
        truepassword = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (username, )
        )
        truepassword = truepassword.fetchone()
        # 比对密码
        if truepassword is not None:
            # Compare passwords
            _, salt, password_hash = truepassword["password"].split("$")
            password = getpassword(password, salt)
            if truepassword["password"] == password:
                session["user_id"] = username
            else:
                abort(403)
        else:
            # Handle the case where the user is not found
            abort(403)

        return flask.redirect(target_url)

    if operation == "create":
        # 从表单拿数据
        username = flask.request.form.get('username')
        password = flask.request.form.get('password')
        fullname = flask.request.form.get('fullname')
        email = flask.request.form.get('email')

        # target_url = flask.request.args.get('target', '/')

        # Unpack flask object
        fileobj = flask.request.files["file"]

        # Check if any of the fields are empty
        if not all([username, password, fullname, email, fileobj]):
            abort(400)

        filename = save_file(fileobj)
        storepassword = getpassword(password)
        connection.execute(
            "INSERT INTO users(username, fullname, email, filename, password) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, storepassword)
        )
        connection.commit()

        session['user_id'] = username
        # Redirect to target URL
        return flask.redirect(target_url)

    if operation == 'delete':
        if 'user_id' not in session:
            abort(403)
        postimgs = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (session["user_id"], )
        )
        postimgs = postimgs.fetchall()
        postimg_urls = [postimg["filename"] for postimg in postimgs]
        for postimgurl in postimg_urls:
            storepath = insta485.app.config["UPLOAD_FOLDER"] / \
                pathlib.Path(postimgurl)
            if os.path.isfile(storepath):
                os.remove(storepath)

        userimgs = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (session["user_id"], )
        )
        userimgs = userimgs.fetchall()
        userimg_urls = [userimg["filename"] for userimg in userimgs]
        for userimgurl in userimg_urls:
            storepath = insta485.app.config["UPLOAD_FOLDER"] / \
                pathlib.Path(userimgurl)
            if os.path.isfile(storepath):
                os.remove(storepath)

        connection.execute(
            "DELETE FROM users WHERE username=?",
            (session["user_id"], )
        )
        connection.commit()
        # 登出
        session.pop('user_id', None)
        return flask.redirect(target_url)

    if operation == "edit_account":
        if "user_id" not in session:
            abort(403)

        fullname = flask.request.form.get('fullname')
        email = flask.request.form.get('email')
        connection.execute(
            "UPDATE users SET email =?, fullname=? WHERE username = ?",
            (email, fullname, session["user_id"])
        )

        fileobj = flask.request.files["file"]

        # Check if any of the fields are empty
        if not all([fullname, email]):
            abort(400)

        if fileobj and fileobj.filename:
            filename = save_file(fileobj)

            userimgs = connection.execute(
                "SELECT filename FROM users WHERE username = ?",
                (session["user_id"], )
            )
            userimgs = userimgs.fetchall()
            userimg_urls = [userimg["filename"] for userimg in userimgs]
            for userimgurl in userimg_urls:
                storepath = insta485.app.config["UPLOAD_FOLDER"] / \
                    pathlib.Path(userimgurl)
                if os.path.isfile(storepath):
                    os.remove(storepath)

            connection.execute(
                "UPDATE users SET filename = ? WHERE username = ?",
                (filename, session["user_id"], )
            )
            connection.commit()

        return flask.redirect(target_url)

    if operation == "update_password":

        if "user_id" not in session:
            abort(403)

        password = flask.request.form.get('password')
        new_password1 = flask.request.form.get('new_password1')
        new_password2 = flask.request.form.get('new_password2')

        if not all([password, new_password1, new_password2]):
            abort(400)

        truepassword = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (session["user_id"], )
        )
        truepassword = truepassword.fetchone()
        # 比对密码
        if truepassword is not None:
            _, salt, password_hash = truepassword["password"].split("$")
            password = getpassword(password, salt)
            if truepassword["password"] != password:
                abort(403)
        else:
            # Handle the case where the user is not found
            abort(403)

        if new_password1 != new_password2:
            abort(401)

        newpassword_hash = getpassword(new_password1)

        connection.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (newpassword_hash, session["user_id"], )
        )
        connection.commit()
        return flask.redirect(target_url)
