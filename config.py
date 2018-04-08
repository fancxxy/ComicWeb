#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import environ


class Config(object):
    SECRET_KEY = 'comic web'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    COMICS_PER_PAGE = 8
    CHAPTERS_PER_PAGE = 30
    RESOURCE_HOME = 'app/static/resources'
    RESOURCE_MODE = 'web'
    UPDATE_HOURS = 4

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('MYSQL_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'dev': DevConfig,
}
