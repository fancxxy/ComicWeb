#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL
from comicd import Comic, ComicdError


class SubscribeForm(FlaskForm):
    url = StringField('Comic URL:', validators=[DataRequired(), URL()], render_kw={'placeholder': 'input comic url'})
    submit = SubmitField('订阅')

    def validate_url(self, field):
        try:
            Comic.find(field.data)
        except ComicdError:
            raise ValidationError('Only support {}'.format(' '.join(list(Comic.support()))))
