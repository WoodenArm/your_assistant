from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.cheatsheet import bp
from app.extensions import db
from app.models.cheatsheet import Cheatsheet
from app.send_email.send_email import send_email
from app.articles.secure_filename import secure_filename

import os

@bp.route('/index')
@login_required
def index():
    cheatsheets = Cheatsheet.query.all()
    list_cheatsheets = []

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
            list_cheatsheets.append((id, title, path, disabled))

    return render_template('cheatsheet/index.html', cheatsheets=list_cheatsheets)



@bp.route('/edit_cheatsheet/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cheatsheet(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)

    if request.method == 'POST':
        cheatsheet.title = request.form.get('title')
        cheatsheet.content = request.form.get('content')
        public_access = request.form.get('public_access')

        # preparation of information from the switch
        if public_access == 'on':
            cheatsheet.public_access = True
        else:
            cheatsheet.public_access = False

        if current_user.username != cheatsheet.author:
            flash("You have no permission to make changes!", 'flash_attention')
            return redirect(url_for('cheatsheet.edit_cheatsheet', id=cheatsheet.id))
        
        # making changes to the cheatsheet
        title = secure_filename(cheatsheet.title)
        content = cheatsheet.content
        filename = os.path.join('app', 'static', 'cheatsheets', f'{title}.txt')
        with open(filename, 'w', encoding='utf-8', newline='') as file_object:
            string = file_object.write(content)
        file_path = filename
        subject = f'Changes made to cheatsheet "{title}".'
        # send_email(file_path, subject)

        db.session.commit()

        flash("Your changes have been saved.", 'flash_success')
        return redirect(url_for('cheatsheet.edit_cheatsheet', id=cheatsheet.id))

    content = cheatsheet.content
    title = cheatsheet.title
    number = cheatsheet.id
    
    # setting switch depending on an entry in the database
    if cheatsheet.public_access:
        public_access = 'checked'
    else:
        public_access = ''

    return render_template('cheatsheet/edit_cheatsheet.html', content=content, title=title, id=number, public_access=public_access)


@bp.route('/add_cheatsheet', methods=['GET', 'POST'])
@login_required
def add_cheatsheet():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        public_access = request.form.get('public_access')
        author = current_user.username

        if public_access == 'on':
            public_access = True
        else:
            public_access = False

        title = f'{title} author {current_user.username}'
        title = secure_filename(title)

        title_exists = Cheatsheet.query.filter_by(title=title).first()
        if title_exists:
            flash("This cheatsheet already exists. Please choose a new title.", 'flash_attention')
            return redirect(url_for('cheatsheet.add_cheatsheet'))

        # make file .txt to send by email
        filename = os.path.join('app', 'static', 'cheatsheets', f'{title}.txt')
        with open(filename, 'w', encoding='utf-8', newline='') as file_object:
            string = file_object.write(content)
        file_path = filename
        subject = f'"{title}" cheatsheet has been added to the data store.'
        # send_email(file_path, subject)

        new_cheatsheet = Cheatsheet(title=title, content=content, author=author, public_access=public_access)
        db.session.add(new_cheatsheet)
        db.session.commit()

        flash('The cheatsheet added successfully.', 'flash_success')
        return redirect(url_for('cheatsheet.index'))

    return render_template('cheatsheet/add_cheatsheet.html')



@bp.route('/del_request/<int:id>')
@login_required
def del_request(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)
    title=cheatsheet.title
    if current_user.username != cheatsheet.author:
        flash("You do not have permission to delete!!", 'flash_attention')
        return redirect(url_for('cheatsheet.index'))
    return render_template('cheatsheet/del_cheatsheet.html', title=title, id=id)

@bp.route('/del_cheatsheet/<int:id>')
@login_required
def del_cheatsheet(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)
    title=cheatsheet.title

    # deleting a file from a folder
    path = os.path.join('app', 'static', 'cheatsheets', f'{title}.txt')
    if os.path.exists(path):
        os.remove(path)

    db.session.delete(cheatsheet)
    db.session.commit()

    flash(f'The cheatsheet { title } has been successfully deleted.', 'flash_success')
    return redirect(url_for('cheatsheet.index'))
