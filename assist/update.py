#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.models import Comic
from app import db


def update_comics():
    with db.app.app_context():
        [comic.update() for comic in Comic.query.all()]
