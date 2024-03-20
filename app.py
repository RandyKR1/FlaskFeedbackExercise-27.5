from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import UserForm, LoginForm
# from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()
connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        
        new_user = User.register(first_name, last_name, email, username, password)
        
        db.session.add(new_user)
        db.session.commit()
        flash(f'Welcome {new_user.username}! Thank you for joining us :)', 'success')
        session['user_id'] = new_user.id
    
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
    
        user = User.authenticate(username,password)
    
        if user:
            flash(f'Welcome back {user.username}!', 'success')
            session['user_id'] = user.id
            return redirect('/secret')
        else:
            form.username.errors = ['invalid username / password']
    
    return render_template('/login.html', form=form)

@app.route('/secret')
def secret():
    return render_template('/secret.html')

@app.route('/logout')
def lougout_user():
    session.pop('user_id')
    flash('Succesfully Logged Out', 'success')
    return redirect('/')