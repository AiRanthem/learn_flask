from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm
@app.route('/')
@app.route('/index')
def index():
    user = {'username':'zty'}
    posts = [
        {
            'author':{'username':'John'},
            'body':"I'm John"
        },
        {
            'author':{'username':'zty'},
            'body':"I'm zty"
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember = {}'
            .format(form.username.data, form.remember_me.data)
        )
        return redirect(url_for('index'))
    return render_template('login.html',title='Sign In', form=form)