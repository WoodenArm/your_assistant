from flask import Flask
from config import Config
from app.extensions import db
from flask_migrate import Migrate

from flask_login import LoginManager


migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints here
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.articles import bp as articles_bp
    app.register_blueprint(articles_bp, url_prefix='/articles')

    from app.cheatsheet import bp as cheatsheet_bp
    app.register_blueprint(cheatsheet_bp, url_prefix='/cheatsheet')

  
    return app

