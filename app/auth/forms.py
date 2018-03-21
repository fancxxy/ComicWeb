#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField('邮箱地址:', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'placeholder': '输入邮件地址'})
    password = PasswordField('密码:', validators=[DataRequired()], render_kw={'placeholder': '输入密码'})
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')
