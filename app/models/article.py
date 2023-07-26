from app.extensions import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    path_article = db.Column(db.String(150), nullable=False)
    tags = db.Column(db.String(300))
    author = db.Column(db.String(150), nullable=False)
    public_access = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Article "{self.title}">'
