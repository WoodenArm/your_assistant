from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.cheatsheet import bp
from app.extensions import db
from app.models.cheatsheet import Cheatsheet

import os

@bp.route('/index')
@login_required
def index():
    cheatsheets = Cheatsheet.query.all()
    return render_template('cheatsheet/index.html', cheatsheets=cheatsheets)


@bp.route('/edit_cheatsheet/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cheatsheet(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)

    if request.method == 'POST':
        cheatsheet.title = request.form.get('title')
        cheatsheet.content = request.form.get('content')

        if current_user.username != cheatsheet.author:
            flash("You have no permission to make changes!")
            return redirect(url_for('cheatsheet.index'))

        db.session.commit()

        flash("Your changes have been saved.")
        return redirect(url_for('cheatsheet.edit_cheatsheet', id=cheatsheet.id))

    content = cheatsheet.content
    title = cheatsheet.title
    number = cheatsheet.id

    return render_template('cheatsheet/edit_cheatsheet.html', content=content, title=title, id=number)


@bp.route('/add_cheatsheet', methods=['GET', 'POST'])
@login_required
def add_cheatsheet():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user.username

        title_exists = Cheatsheet.query.filter_by(title=title).first()
        if title_exists or len(title) == 0:
            flash("This cheatsheet already exists. Please choose a new title.")
            return redirect(url_for('cheatsheet.add_cheatsheet'))

        new_cheatsheet = Cheatsheet(title=title, content=content, author=author)
        db.session.add(new_cheatsheet)
        db.session.commit()

        flash('The cheatsheet added successfully.')
        return redirect(url_for('cheatsheet.add_cheatsheet'))

    return render_template('cheatsheet/add_cheatsheet.html')


@bp.route('/del_request/<int:id>')
@login_required
def del_request(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)
    title=cheatsheet.title
    if current_user.username != cheatsheet.author:
        flash("You do not have permission to delete!!")
        return redirect(url_for('cheatsheet.index'))
    return render_template('cheatsheet/del_cheatsheet.html', title=title, id=id)

@bp.route('/del_cheatsheet/<int:id>')
@login_required
def del_cheatsheet(id):
    cheatsheet = Cheatsheet.query.get_or_404(id)
    title=cheatsheet.title

    db.session.delete(cheatsheet)
    db.session.commit()

    flash(f'The cheatsheet { title } has been successfully deleted.')
    return redirect(url_for('cheatsheet.index'))
