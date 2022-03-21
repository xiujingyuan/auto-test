import hashlib
from datetime import timedelta

from flask import render_template, redirect, request, url_for, flash, jsonify, json, current_app, session
from flask_login import login_user, logout_user, login_required, \
    current_user

import app
from app import db, csrf
from app.auth import auth
from app.common.components.email import send_email
from app.models.UserModel import User
import requests
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('customer.index'))
    return render_template(current_app.config["THEME_URL"] +'auth/unconfirmed.html')


# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user is not None and user.verify_password(form.password.data):
#             login_user(user, form.remember_me.data)
#             return redirect(request.args.get('next') or url_for('customer.index'))
#         flash('Invalid username or password.')
#     return render_template(current_app.config["THEME_URL"] +'auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('customer.index'))


@auth.route('/login')
def login():
    url = current_app.config.get("PASSPORT_HEADER") + current_app.config.get("PASSPORT_CODE_PATH").format(
        current_app.config.get("PASSPORT_CLIEND_ID"),
        current_app.config.get("PASSPORT_CALLBACK_URL"))
    session.permanent = True
    return redirect(url)


@auth.route('/kuainiu/user/auth')
@csrf.exempt
def auth_callback():
    data = {}
    if "code" in request.args:
        code = request.args["code"]
        jsondata = {
            "grant_type": "authorization_code",
            "client_id": current_app.config.get("PASSPORT_CLIEND_ID"),
            "client_secret": current_app.config.get("PASSPORT_CLIENT_SECRET"),
            "redirect_uri": current_app.config.get("PASSPORT_CALLBACK_URL"),
            "code": code
        }

        url = current_app.config.get("PASSPORT_HEADER") + current_app.config.get("PASSPORT_ACCESS_TOKEN_PATH")
        headers = {'content-type': 'application/json'}
        req = requests.post(url, data=json.dumps(jsondata), headers=headers, verify=False)

        req_data = req.json()

        if "access_token" not in req_data:
            data = {"code": 3, "message": "获取权限失败", "data": req_data}
        else:
            user_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + req_data['access_token']}
            user_url = current_app.config.get("PASSPORT_HEADER") + current_app.config.get("PASSPORT_USER_PATH")

            req_user = requests.get(user_url, data=json.dumps({}), headers=user_headers, verify=False)
            if hasattr(req_user, "json") and "code" in req_user.json():
                if req_user.json()["code"] == 1 and "data" in req_user.json():
                    user_info = req_user.json()["data"]
                    if filter(lambda x: x not in user_info, ["name", "email", "avatar"]):
                        query_user = User.query.filter(User.email == user_info["email"]).all()
                        if not query_user:
                            user = User()
                            user.username = user_info["name"]
                            user.email = user_info["email"]
                            user.avatar = user_info["avatar"]
                            user.confirmed = 1
                            user.role_id = 1
                            user.password_hash = req_data['access_token'][5:25]
                            db.session.add(user)
                            db.session.flush()
                        else:
                            user = query_user[0]

                        login_user(user)

                        session.permanent = True
                        # app.permanent_session_lifetime = timedelta(minutes=10)

                        # current_app.refer_url = None if not hasattr(current_app,
                        # "refer_url") else current_app.refer_url
                        # current_app.logger.info(current_app.refer_url)
                        return redirect(request.args.get('next') or request.referrer or
                                        url_for('customer.index'))
                    else:
                        data = {"code": 6, "message": "获取用户错误", "data": req_user.json()}
                else:
                    data = {"code": 4, "message": "获取用户错误", "data": req_user.json()}
            else:
                data = {"code": 5, "message": "获取用户错误", "data": req_user.text}
    else:
        data = {"code": 2, "message": "获取权限失败"}

    return jsonify(data)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.flush()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template(current_app.config["THEME_URL"] +'auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('customer.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('customer.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('customer.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.flush()
            flash('Your password has been updated.')
            return redirect(url_for('customer.index'))
        else:
            flash('Invalid password.')
    return render_template(current_app.config["THEME_URL"] +"auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('customer.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template(current_app.config["THEME_URL"] +'auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('customer.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('customer.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('customer.index'))
    return render_template(current_app.config["THEME_URL"] +'auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('customer.index'))
        else:
            flash('Invalid email or password.')
    return render_template(current_app.config["THEME_URL"] +"auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('customer.index'))
