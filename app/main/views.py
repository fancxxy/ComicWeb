#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from hashlib import md5
from datetime import datetime
from os import listdir

from flask import render_template, redirect, url_for, current_app, flash, request
from flask_login import current_user, login_required
from os.path import join, splitext, exists

from app import db
from . import main
from .forms import SubscribeForm
from comicd import Comic as cc, Chapter as cr, Config as cg
from ..models import Comic, Chapter, Image
from ..utils import crop_cover, quote


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SubscribeForm()
    if form.validate_on_submit():
        comic = Comic.query.filter_by(url=form.url.data).first()
        if comic:
            current_user.subscribe(comic)
            flash('Subscribe succeed')
            return redirect(url_for('main.index'))
        else:
            c = cc(form.url.data)
            if c.init():
                hash = md5((c.instance.name + c.title).encode('utf-8')).hexdigest()
                comic = Comic(url=c.url, title=c.title, interface=c.instance.name,
                              cover=hash + '.jpg', summary=c.summary, newest=c.chapters[-1][0],
                              updates=datetime.utcnow())
                r, f = c.download_cover('app/static/covers', comic.cover)
                if r:
                    crop_cover(f)
                current_user.subscribe(comic)
                db.session.add(comic)
                db.session.commit()
                for title, url in c.chapters:
                    chapter = Chapter(title=title, comic_title=comic.title, interface=comic.interface, url=url,
                                      comic_id=comic.id)
                    db.session.add(chapter)
                db.session.commit()
                flash('Subscribe succeed')
                return redirect(url_for('main.index'))
            else:
                flash('Subscribe failed')
    page = request.args.get('page', 1, type=int)
    # pagination = db.session.query(Comic). \
    #     filter(Comic.id == Subscriber.comic_id). \
    #     filter(User.id == Subscriber.user_id). \
    #     filter(User.id == current_user.id).paginate(page, per_page=20, error_out=False)
    # comics = pagination.items
    pagination = current_user.comics.paginate(page, per_page=current_app.config['COMICS_PER_PAGE'], error_out=False)
    comics = [item.comic for item in pagination.items]
    return render_template('index.html', comics=comics, pagination=pagination, form=form)


@main.route('/comics/<id>')
@login_required
def comic(id):
    comic = Comic.query.get_or_404(id)
    # comic.update()
    page = request.args.get('page', 1, type=int)
    pagination = comic.chapters.order_by(db.desc(Chapter.id)).paginate(page, per_page=current_app.config['CHAPTERS_PER_PAGE'], error_out=False)
    chapters = pagination.items
    return render_template('comic.html', comic=comic, chapters=chapters, pagination=pagination)


@main.route('/comics/<id>/<cid>')
@login_required
def chapter(id, cid):
    chapter = Chapter.query.filter(Chapter.id == cid and Chapter.comic_id == id).first()
    if not chapter.path:
        c = cr(chapter.url)
        if c.init():
            c.download()
        count, chapter.path = 1, join(cg.home, quote(chapter.comic_title), quote(chapter.title))
        if exists(chapter.path):
            files = sorted([i for i in listdir(chapter.path) if splitext(i)[1] == '.jpg'], key=lambda x: int(x[:-4]))
            for file in files:
                image = Image(comic_id=id, chapter_id=cid, image_id=count,
                              path=join(chapter.comic_title, chapter.title, file))
                count += 1
                db.session.add(image)

    images = Image.query.filter_by(comic_id=id, chapter_id=cid).order_by(Image.image_id).all()
    return render_template('chapter.html', chapter=chapter, images=images, previous=request.referrer)
