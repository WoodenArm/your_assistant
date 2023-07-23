from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.articles import bp
from app.extensions import db
from app.models.article import Article
from app.articles.secure_filename import secure_filename
from app.models.cheatsheet import Cheatsheet

import os


@bp.route('/')
@login_required
def index():
    articles = Article.query.all()
    return render_template('articles/index.html', articles=articles)


@bp.route('/show_article/<int:id>')
@login_required
def show_article(id):
    article = Article.query.filter_by(id=id).first()
    title = article.title
    name = article.path_article
    path = url_for('static', filename=f'articles/{name}')
    return render_template('articles/article.html', title=title, path=path, id=id)


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    tag = request.form.get('tag')
    if len(tag) >= 2:
        articles = Article.query.all()
        articles_filter = []
        for i in articles:
            if tag in i.tags:
                articles_filter.append(i)
            if tag in i.title.lower():
                articles_filter.append(i)

        cheatsheets = Cheatsheet.query.all()
        cheatsheets_filter = []
        for i in cheatsheets:
            if tag in i.title:
                cheatsheets_filter.append(i)
            if tag in i.content:
                cheatsheets_filter.append(i)
        matches = len(articles_filter) + len(cheatsheets_filter)
        return render_template('articles/search.html', articles=articles_filter, cheatsheets=cheatsheets_filter, matches=matches, tag=tag)
    else:
        return render_template('articles/search.html', matches='0', tag=tag)


def allowed_file(filename):
    a = filename.rsplit('.', 1)[1] in set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])

    articles = Article.query.all()
    article_titles =[]
    for i in articles:
        article_titles.append(i.title)
    filename = (filename.split('.', 1)[0]).replace(' ', '_')
    b = filename.split('.', 1)[0] not in article_titles
    return a and b


@bp.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Can't read file.", 'flash_attention')  
            return redirect(request.url)  
        file = request.files['file']
        if file.filename == '':
            flash('You have not selected an article.', 'flash_attention')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filename = file.filename
            file.save(os.path.join('app', 'static', 'articles', filename))

            tags = request.form.get('tags')

            author = current_user.username

            new_article = Article(title=filename.rsplit('.', 1)[0], path_article=filename, tags=tags, author=author)
            db.session.add(new_article)
            db.session.commit()

            flash('The article added successfully.', 'flash_success')

            return redirect(url_for('articles.add_article'))
        flash('The file name is repeated or the format is not allowed.')
    return render_template('articles/add_article.html')


@bp.route('/del_request/<int:id>')
@login_required
def del_request(id):
    article = Article.query.filter_by(id=id).first()
    title = article.title
    if current_user.username != article.author:
        flash("You do not have permission to delete!!", 'flash_attention')
        return redirect(url_for('articles.index'))
    return render_template('articles/del_article.html', title=title, id=id)




@bp.route('/del_article/<int:id>')
@login_required
def del_article(id):
    article = Article.query.filter_by(id=id).first()
    title = article.title
    filename = article.path_article

    path = os.path.join('app', 'static', 'articles', filename)
    os.remove(path)

    db.session.delete(article)
    db.session.commit()


    flash(f'The article { title } has been successfully deleted.', 'flash_success')
    return redirect(url_for('articles.index'))
