from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Board(db.Model):
    __tablename__ = 'boards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    category = db.Column(db.String(64), nullable=False)
    nsfw = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    threads = db.relationship('Thread', backref='board', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Board /{self.slug}/ - {self.name}>'


class Thread(db.Model):
    __tablename__ = 'threads'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128))
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    sticky = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    
    posts = db.relationship('Post', backref='thread', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Thread {self.id} on /{self.board.slug}/>'


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    poster_name = db.Column(db.String(64), default="Anonymous")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    
    images = db.relationship('Image', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.id} in Thread {self.thread_id}>'


class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    mega_url = db.Column(db.String(512), nullable=False)  # URL to the file on Mega.nz
    public_url = db.Column(db.String(512), nullable=False)  # URL for displaying the image
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Image {self.id} in Post {self.post_id}>'


class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='votes')
    thread = db.relationship('Thread', backref='votes')
    post = db.relationship('Post', backref='votes')
    
    def __repr__(self):
        target = f'Thread {self.thread_id}' if self.thread_id else f'Post {self.post_id}'
        return f'<Vote by User {self.user_id} on {target}>'


class CaptchaToken(db.Model):
    __tablename__ = 'captcha_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    solution = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<CaptchaToken {self.token}>'
