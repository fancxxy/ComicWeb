#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Comic, Subscriber, Image, Chapter

app = create_app('dev')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Comic=Comic, Subscriber=Subscriber, Chapter=Chapter, Image=Image)
