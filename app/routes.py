from app import app
from app import db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from datetime import datetime

# for login
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

# for twitte
from app.forms import PostForm
from app.models import Post

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

def get_posts(base_url, show_all = True):
    page = request.args.get('page', 1, type=int)
    if show_all:
        posts = Post.query.order_by(Post.timestamp.desc())
    else:
        posts = current_user.followed_posts()
    posts = posts.paginate(
                page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(base_url, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for(base_url, page=posts.prev_num) \
        if posts.has_prev else None
    return page, next_url, prev_url, posts

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page, next_url, prev_url, posts = get_posts('index', show_all=False)
    return render_template('index.html', 
                            title='Home', 
                            posts=posts.items, 
                            form = form, 
                            next_url=next_url, 
                            prev_url=prev_url,
                            page=page)

@app.route('/explore')
@login_required
def explore():
    page, next_url, prev_url, posts = get_posts('explore')
    return render_template("index.html", 
                            title='Explore', 
                            posts=posts.items,
                            next_url=next_url, 
                            prev_url=prev_url,
                            page=page)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': # 确保重定向到自己的站点，避免被攻击
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# for register
from app.forms import RegistrationForm
@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, register success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# for profile
from app.forms import EditProfileForm
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, page=page)

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form =EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="Edit Profile", form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))
