from flask import current_app
from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from datetime import datetime

# for login
from app.auth.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

# for twitte
from app.auth.forms import PostForm
from app.models import Post

# for language
from flask import g
from flask_babel import get_locale
from app.auth import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.local = str(get_locale())

def get_posts(base_url, show_all = True):
    page = request.args.get('page', 1, type=int)
    if show_all:
        posts = Post.query.order_by(Post.timestamp.desc())
    else:
        posts = current_user.followed_posts()
    posts = posts.paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(base_url, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for(base_url, page=posts.prev_num) \
        if posts.has_prev else None
    return page, next_url, prev_url, posts

from guess_language import guess_language
@bp.route('/', methods = ['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body = form.post.data, author = current_user, language = language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('auth.index'))
    page, next_url, prev_url, posts = get_posts('auth.index', show_all=False)
    return render_template('index.html', 
                            title='Home', 
                            posts=posts.items, 
                            form = form, 
                            next_url=next_url, 
                            prev_url=prev_url,
                            page=page)

@bp.route('/explore')
@login_required
def explore():
    page, next_url, prev_url, posts = get_posts('auth.explore')
    return render_template("index.html", 
                            title='Explore', 
                            posts=posts.items,
                            next_url=next_url, 
                            prev_url=prev_url,
                            page=page)

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': # 确保重定向到自己的站点，避免被攻击
            next_page = url_for('auth.index')
        return redirect(next_page)
    return render_template('login.html',title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))

# for register
from app.auth.forms import RegistrationForm
@bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, register success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

# for profile
from app.auth.forms import EditProfileForm
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('auth.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('auth.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, page=page)

@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form =EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="Edit Profile", form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('auth.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('auth.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('auth.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('auth.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('auth.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('auth.user', username=username))

# for reset password
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': 'Nope'})