#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'placeholder': 'Enter email'})
    password = PasswordField('Password:', validators=[DataRequired()], render_kw={'placeholder': 'Enter password'})
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
