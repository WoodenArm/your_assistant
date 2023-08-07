from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.articles import bp
from app.extensions import db
from app.models.article import Article
from app.articles.secure_filename import secure_filename
from app.models.cheatsheet import Cheatsheet
from app.send_email.send_email import send_email

import os


@bp.route('/')
@login_required
def index():
    articles = Article.query.all()

    list_articles = []
    for article in articles:       
        if current_user.username == article.author or article.public_access:
            title = article.title
            name = article.path_article
            path = url_for('static', filename=f'articles/{name}')
            id = article.id
            if current_user.username != article.author:
                disabled = 'disabled'
            else:
                disabled = 'enabled'
            list_articles.append((title, path, id, disabled))       
        
    return render_template('articles/index.html', articles=list_articles)


@bp.route('/show_article/<int:id>', methods=['GET', 'POST'])
@login_required
def show_article(id):
    article = Article.query.get_or_404(id)

    if request.method == 'POST':
        public_access = request.form.get('public_access')

        if public_access == 'on':
            article.public_access = True
        else:
            article.public_access = False

        if current_user.username != article.author:
            flash("You have no permission to make changes!", 'flash_attention')
            return redirect(url_for('articles.show_article', id=article.id))
        
        db.session.commit()

        flash("Your changes have been saved.", 'flash_success')
        return redirect(url_for('articles.show_article', id=article.id))

    if article.public_access:
        public_access = 'checked'
    else:
        public_access = ''

    title = article.title
    name = article.path_article
    path = url_for('static', filename=f'articles/{name}')

    return render_template('articles/article.html', title=title, path=path, id=id, public_access=public_access)


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    tag = request.form.get('tag')
    if len(tag) >= 3:
        articles = Article.query.all()
        articles_filter = []
        for article in articles:
            if current_user.username == article.author or article.public_access:
                title = article.title
                name = article.path_article
                path = url_for('static', filename=f'articles/{name}')
                id = article.id
                # edit button activity
                if current_user.username != article.author:
                    disabled = 'disabled'
                else:
                    disabled = 'enabled'
                if tag in f'{article.tags} {article.title}'.lower():
                    articles_filter.append((title, path, id, disabled))     
        articles_filter = set(articles_filter)

        cheatsheets = Cheatsheet.query.all()
        cheatsheets_filter = []
        for cheatsheet in cheatsheets:       
            if current_user.username == cheatsheet.author or cheatsheet.public_access:
                id = cheatsheet.id
                title = cheatsheet.title
                
                path = url_for('static', filename=f'cheatsheets/{title}.txt')
                
                # edit button activity
                if current_user.username != cheatsheet.author:
                    disabled = 'disabled'
                else:
                    disabled = 'enabled'
                if tag in f'{cheatsheet.title} {cheatsheet.content}'.lower():
                    cheatsheets_filter.append((id, title, path, disabled))    
               
        cheatsheets_filter = set(cheatsheets_filter)
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

            # preparing a file for sending by email
            file_path = os.path.join('app', 'static', 'articles', filename)
            subject = f'"{filename}" article has been added to the data store..'
            # send_email(file_path, subject)

            tags = request.form.get('tags')

            author = current_user.username
            public_access = request.form.get('public_access')
            if public_access == 'on':
                public_access = True
            else:
                public_access = False

            title=filename.rsplit('.', 1)[0]
            title = f'{title}_author_{current_user.username}'

            new_article = Article(title=title, path_article=filename, tags=tags, author=author, public_access=public_access)
            db.session.add(new_article)
            db.session.commit()

            flash('The article added successfully.', 'flash_success')

            return redirect(url_for('articles.add_article'))
        flash('The file name is repeated or the format is not allowed.', 'flash_attention')
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
