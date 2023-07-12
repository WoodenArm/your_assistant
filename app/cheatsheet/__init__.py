from flask import Blueprint

bp = Blueprint('cheatsheet', __name__)

from app.cheatsheet import routes
