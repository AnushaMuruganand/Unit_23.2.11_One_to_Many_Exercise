"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "SECRET!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route("/")
def home_page():
    """Show recent list of posts, most-recent first."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("homepage.html", posts=posts)

# CUSTOM ERROR PAGE ON 404 STATUS CODE
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
# ------------------------- USER ROUTES -----------------------------

@app.route("/users")
def list_users():
    """ List all users from the database """

    # "order_by()" orders the users by "last_name, first_name"
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("user-listing.html", users = users)

@app.route("/users/new")
def show_user_form():
    """ Show form to create a new user """

    return render_template("user-form.html")


@app.route("/users/new", methods=['POST'])
def create_user():
    """ Create a new user and update the database """

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]
    image_url = image_url if image_url else None

    new_user = User(first_name = first_name, last_name = last_name, image_url = image_url)
    db.session.add(new_user)
    db.session.commit()

    flash(f"User {new_user.full_name} added.")

    return redirect("/users")

@app.route("/users/<int:user_id>")
def show_detail(user_id):
    """ Shows the details of the user, the user clicked on """

    # Get user based off user_id
    user = User.query.get_or_404(user_id)

    return render_template("user-details.html", user = user)

@app.route("/users/<int:user_id>/edit")
def show_edit(user_id):
    """ Show the edit page for a particular user """

    user = User.query.get_or_404(user_id)
    return render_template("user-edit.html", user = user)

@app.route("/users/<int:user_id>/edit", methods = ['POST'])
def edit_user(user_id):
    """Handle form submission for updating an existing user"""

    edit_user = User.query.get_or_404(user_id)
    edit_user.first_name = request.form["first_name"]
    edit_user.last_name = request.form["last_name"]
    edit_user.image_url = request.form["image_url"]

    db.session.add(edit_user)
    db.session.commit()

    flash(f"User {edit_user.full_name} edited.")

    return redirect("/users")

@app.route("/users/<int:user_id>/delete", methods = ['POST'])
def delete_user(user_id):
    """ Delete a user and update the database"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash(f"User {user.full_name} deleted.")

    return redirect("/users")


# ---------------- Post ROUTES ------------------------

@app.route("/users/<int:user_id>/posts/new")
def show_post_form(user_id):
    """ Show form to create a post """

    user = User.query.get_or_404(user_id)

    return render_template("post-form.html", user = user )

@app.route("/users/<int:user_id>/posts/new", methods = ['POST'])
def create_post(user_id):
    """  
    Create a post and update the "posts" table in the database 
    And redirect to user detail page i.e to ROUTE "/users/<user_id>"
    """

    # Get user based off of "user_id"
    user = User.query.get_or_404(user_id)

    title = request.form["title"]
    content = request.form["content"]

    new_post = Post(title = title, content = content, user = user)
    db.session.add(new_post)
    db.session.commit()

    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")

@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """ Show Post Details """

    post = Post.query.get_or_404(post_id)

    return render_template("post-detail.html", post = post)

@app.route("/posts/<int:post_id>/edit")
def show_post_edit(post_id):
    """ Shpw Post Edit Form """

    post = Post.query.get_or_404(post_id)
    return render_template("post-edit.html", post = post)

@app.route("/posts/<int:post_id>/edit", methods = ['POST'])
def edit_post(post_id):
    """ Edit Post and update in database "posts" table """

    edit_post = Post.query.get_or_404(post_id)
    edit_post.title = request.form["title"]
    edit_post.content = request.form["content"]

    # Update the database
    db.session.add(edit_post)
    db.session.commit()

    flash(f"Post '{edit_post.title}' edited.")

    return redirect(f"/users/{edit_post.user_id}")

@app.route("/posts/<int:post_id>/delete", methods = ['POST'])
def delete_post(post_id):
    """ Delete the Post and update the database """

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")
