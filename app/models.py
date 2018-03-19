#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hashlib import md5
from datetime import datetime
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from comicd import Comic as cc, Chapter as cr
from .utils import crop_cover


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), primary_key=True)
    subscribe_date = db.Column(db.DateTime(), default=datetime.utcnow)


# subscribers = db.Table('subscribers',
#                        db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
#                        db.Column('comic_id', db.Integer, db.ForeignKey('comics.id'), primary_key=True),
#                        db.Column('subscribe_date', db.Date, default=datetime.date))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    comics = db.relationship('Subscriber', backref=db.backref('user', lazy='joined'), lazy='dynamic',
                             cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def subscribe(self, comic):
        if self.comics.filter_by(comic_id=comic.id).first() is None:
            s = Subscriber(user=self, comic=comic)
            db.session.add(s)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comic(db.Model):
    __tablename__ = 'comics'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    interface = db.Column(db.String(32), nullable=False)
    cover = db.Column(db.String(256))
    summary = db.Column(db.Text())
    newest = db.Column(db.String(64))
    updates = db.Column(db.DateTime(), default=None)

    users = db.relationship('Subscriber', backref=db.backref('comic', lazy='joined'), lazy='dynamic',
                            cascade='all, delete-orphan')
    chapters = db.relationship('Chapter', backref='comic', lazy='dynamic')
    __table_args__ = (db.UniqueConstraint('title', 'interface', name='uc_title_interface'),)

    def __repr__(self):
        return '<Comic {} {}>'.format(self.title, self.interface)

    def update(self):
        c = cc(self.url)
        if c.init():
            self.title = c.title
            self.interface = c.instance.name
            self.cover = md5((c.instance.name + c.title).encode('utf-8')).hexdigest() + '.jpg'
            self.summary = c.summary
            self.newest = c.chapters[-1][0]
            self.updates = datetime.utcnow()
            r, f = c.download_cover('app/static/covers', self.cover)
            if r:
                crop_cover(f)
            db.session.add(self)
            # for chapter in self.chapters:
            #     chapter.update()
        else:
            # TODO log error
            pass


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), unique=True, nullable=False)
    title = db.Column(db.String(128))
    interface = db.Column(db.String(32))
    comic_title = db.Column(db.String(128))
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    update_time = db.Column(db.DateTime())
    path = db.Column(db.String(256), default=None)
    __table_args__ = (db.UniqueConstraint('title', 'comic_title', 'interface', name='uc_title_comic_title_interface'),)

    def __repr__(self):
        return '<Chapter {} {} {}>'.format(self.comic_title, self.title, self.interface)

    def update(self):
        c = cr(self.url)
        if c.init():
            self.title = c.ctitle
            self.comic_title = c.title
            self.interface = c.instance.name
            update_time = datetime.utcnow()
            db.session.add(self)
        else:
            # TODO log error
            pass


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    image_id = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(256), nullable=False, unique=True)

