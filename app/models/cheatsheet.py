from app.extensions import db

class Cheatsheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text(3000), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    public_access = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'<Cheatsheet "{self.title}">'
