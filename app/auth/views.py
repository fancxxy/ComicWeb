#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_login import login_user, login_required, logout_user, current_user
from flask import redirect, request, url_for, flash, render_template
from app.models import User
from . import auth
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('错误的邮件地址或者密码', 'warning')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出', 'info')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
