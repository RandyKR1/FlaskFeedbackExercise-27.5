from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, DeleteForm, FeedbackForm
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
        return redirect(f'/users/{session["user_id"]}')
    
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
            return redirect(f'/users/{user.id}')
        else:
            flash('user not found, check username/password combination', 'danger')
            return redirect('/login')
    
    return render_template('/login.html', form=form)

@app.route('/users/<int:id>')
def user_profile(id):
    if 'user_id' not in session or id != session['user_id']:
        flash('unauthorized, please log in first', 'danger')
        session.pop('user_id')
        return redirect('/login')

    user = User.query.get(id)
    form = DeleteForm()
    
    return render_template("user.html", user=user, form=form)
    
@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    if 'user_id' not in session or id != session['user_id']:
        flash('unauthorized, please log in first', 'danger')
        session.pop('user_id')
        return redirect('/login')
    
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    
    return redirect('/login')
    
@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('Succesfully Logged Out', 'success')
    return redirect('/')

@app.route('/users/<int:id>/feedback/new', methods=['GET', 'POST'])
def add_feedback(id):
    if 'user_id' not in session or id != session['user_id']:
        flash('unauthorized, please log in first', 'danger')
        session.pop('user_id')
        return redirect('/login')
    
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
        user = User.query.get(id)
        new_feedback = Feedback(title=title, content=content, username=user.username)
        
        db.session.add(new_feedback)
        db.session.commit()
        
        return redirect(f"/users/{user.id}")
    else:
        return render_template('/add.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods = ['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    
    fb_user = User.query.filter_by(username=feedback.username).first()
    
    if 'user_id' not in session or fb_user.id != session['user_id']:
        flash('unauthorized, please log in first', 'danger')
        session.pop('user_id')
        return redirect('/login')
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{session["user_id"]}')

    return render_template("/update.html", form=form, feedback=feedback)
    
@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    
    fb_user = User.query.filter_by(username=feedback.username).first()
    
    if 'user_id' not in session or fb_user.id != session['user_id']:
        flash('unauthorized, please log in first', 'danger')
        session.pop('user_id')
        return redirect('/login')
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f'/users/{session["user_id"]}')