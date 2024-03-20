from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name =  db.Column(db.String(30), nullable=False)
    last_name =  db.Column(db.String(30), nullable=False)
    email =  db.Column(db.String(50), nullable=False, unique=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password =  db.Column(db.Text, nullable=False)
    
    
    
    @classmethod
    def register(cls, fn, ln, email, username, pwd):
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')
        return cls(first_name=fn, last_name=ln, email=email, username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, pwd):
        u = User.query.filter_by(username=username).first()
        
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        
        
        
def connect_db(app):
    db.app = app
    db.init_app(app)