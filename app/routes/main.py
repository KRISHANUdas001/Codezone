from flask import Blueprint, render_template
from app.models.post import Post

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', title='Home', posts=posts)