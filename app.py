"""Blogly application."""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'
app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


@app.route('/')
def root():
    """Homepage redirects to list of users. Expecting this to change in later parts of exercise."""

    return redirect("/users")


##############################################################################
# User routes

@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)

@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('users/new.html')

@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)

@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

##############################################################################
# Post routes

@app.route('/users/<int:user_id>/posts/new', methods=["GET"])
def users_new_post(user_id):
    """Show a form to add new post for an existing user"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template('users/new_post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def users_add_new_post(user_id):
    """Handle form submission for user's new post"""

    user = User.query.get_or_404(user_id)
    new_post = Post(
        title = request.form['title'],
        content = request.form['content'],
        author_id = user.id)

    for chosen_tag in request.form.getlist('selected-tags'):
        tag = Tag.query.filter_by(name=chosen_tag).first()
        new_post.tags.append(tag)
    
    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a specific post with Edit and Delete buttons and tags"""

    post = Post.query.get_or_404(post_id)
    user = User.query.get(post.author_id)

    return render_template('posts/show.html', post=post, user=user)

@app.route('/posts/<int:post_id>/edit', methods=["GET"])
def posts_edit(post_id):
    """Show a form to edit post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    return render_template('posts/edit.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_edit_submit(post_id):
    """Handle form submission for post edit"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    prev_tags = PostTag.query.filter(PostTag.post_id==post_id).all()
    for prev_tag in prev_tags:
        db.session.delete(prev_tag)
    db.session.commit()

    for chosen_tag in request.form.getlist('selected-tags'):
        tag = Tag.query.filter_by(name=chosen_tag).first()
        post.tags.append(tag)

    db.session.add(post)
    db.session.commit()

    return redirect(f"/posts/{post_id}")

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_delete(post_id):
    """Handle button click for deleting a post"""

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.author_id}")

##############################################################################
# Tag routes

@app.route('/tags')
def tags_index():
    """Show a page with list of all tags"""

    tags = Tag.query.all()

    return render_template('tags/index.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def tag_detail(tag_id):
    """Show tag details with Edit and Delete buttons"""

    tag = Tag.query.get_or_404(tag_id)

    return render_template('tags/show.html', tag=tag)

@app.route('/tags/new', methods=["GET"])
def new_tag():
    """Show a form to add new tag"""

    return render_template('tags/new.html')

@app.route('/tags/new', methods=["POST"])
def add_new_tag():
    """Handle form submission for new tag"""

    new_tag = Tag(name = request.form['tag-name'])

    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit', methods=["GET"])
def tag_edit(tag_id):
    """Show a form to edit tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/edit.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tag_edit_submit(tag_id):
    """Handle form submission for tag edit"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['tag-name']

    db.session.add(tag)
    db.session.commit()

    return redirect(f"/tags/{tag_id}")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tag_delete(tag_id):
    """Handle button click for deleting a tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")