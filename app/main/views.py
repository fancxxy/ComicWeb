#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from hashlib import md5
from os import listdir

from flask import render_template, redirect, url_for, current_app, flash, request
from flask_login import current_user, login_required
from os.path import join, splitext, exists

from app import db
from . import main
from .forms import SubscribeForm
from comicd import Comic as cc, Chapter as cr, Config as cg
from ..models import Comic, Chapter, Image, Subscriber
from ..utils import crop_cover, quote


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SubscribeForm()
    if form.validate_on_submit():
        comic = Comic.query.filter_by(url=form.url.data).first()
        if comic:
            current_user.subscribe(comic)
            flash('订阅成功', 'success')
            return redirect(url_for('main.index'))
        else:
            c = cc(form.url.data)
            if c.init():
                hash = md5((c.instance.name + c.title).encode('utf-8')).hexdigest()
                comic = Comic(url=c.url, title=c.title, interface=c.instance.name, cover=hash + '.jpg',
                              summary=c.summary)
                r, f = c.download_cover('app/static/covers', comic.cover)
                if r:
                    crop_cover(f)
                current_user.subscribe(comic)
                db.session.add(comic)
                db.session.commit()
                index = 1
                for title, url in c.chapters:
                    chapter = Chapter(title=title, comic_title=comic.title, interface=comic.interface, url=url,
                                      comic_id=comic.id, chapter_no=index)
                    db.session.add(chapter)
                    index += 1
                db.session.commit()
                chapter = Chapter.query.filter_by(comic_id=comic.id).order_by(db.desc(Chapter.id)).first()
                comic.newest_chapter_id, comic.newest_chapter_title = chapter.id, chapter.title
                db.session.add(comic)
                db.session.commit()
                flash('订阅成功', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('订阅失败', 'danger')
    page = request.args.get('page', 1, type=int)
    pagination = current_user.comics.paginate(page, per_page=current_app.config['COMICS_PER_PAGE'], error_out=False)
    comics = [item.comic for item in pagination.items]
    return render_template('index.html', comics=comics, pagination=pagination, form=form)


@main.route('/unsubscribe/<id>')
@login_required
def unsubscribe(id):
    subscriber = Subscriber.query.filter_by(user_id=current_user.id, comic_id=id).first()
    if subscriber:
        db.session.delete(subscriber)
    flash('取消订阅', 'info')
    return redirect(url_for('main.index'))


@main.route('/comics/<id>')
@login_required
def comic(id):
    comic = Comic.query.get_or_404(id)
    comic.update()
    page = request.args.get('page', 1, type=int)
    pagination = comic.chapters.order_by(db.desc(Chapter.id)).paginate(page,
                                                                       per_page=current_app.config['CHAPTERS_PER_PAGE'],
                                                                       error_out=False)
    chapters = pagination.items
    last_chapter = Chapter.query.filter_by(id=Subscriber.query.filter_by(user_id=current_user.id,
                                                                         comic_id=id).first().last_chapter_id).first()
    newest_chapter = Chapter.query.filter_by(id=comic.newest_chapter_id).first()
    return render_template('comic.html', comic=comic, chapters=chapters, pagination=pagination,
                           last_chapter=last_chapter, newest_chapter=newest_chapter)


@main.route('/comics/<id>/<no>')
@login_required
def chapter(id, no):
    chapter = Chapter.query.filter_by(comic_id=id, chapter_no=no).first()
    if not chapter.path:
        c = cr(chapter.url)
        if c.init():
            c.download()
        count, chapter.path = 1, join(cg.home, quote(chapter.comic_title), quote(chapter.title))
        if exists(chapter.path):
            files = sorted([i for i in listdir(chapter.path) if splitext(i)[1] == '.jpg'], key=lambda x: int(x[:-4]))
            for file in files:
                image = Image(comic_id=id, chapter_id=chapter.id, image_no=count,
                              path=join(chapter.comic_title, chapter.title, file))
                db.session.add(image)
                count += 1

    subscriber = Subscriber.query.filter_by(user_id=current_user.id, comic_id=chapter.comic_id).first()
    subscriber.last_chapter_id = chapter.id
    db.session.add(subscriber)
    images = Image.query.filter_by(comic_id=id, chapter_id=chapter.id).order_by(Image.image_no).all()
    return render_template('chapter.html', chapter=chapter, images=images, previous=request.referrer)
