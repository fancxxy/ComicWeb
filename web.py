#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Comic, Subscriber, Image, Chapter

app = create_app('dev')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    user = User.query.filter_by(username='comic').first()
    if not user:
        u = User(email='comic@comic.com', username='comic', password='comic', confirmed=True)
        db.session.add(u)
        db.session.commit()
    return dict(db=db, User=User, Comic=Comic, Subscriber=Subscriber, Chapter=Chapter, Image=Image)
