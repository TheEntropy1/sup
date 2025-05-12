from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask import current_app

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class NewThreadForm(FlaskForm):
    subject = StringField('Subject', validators=[Optional(), Length(max=128)])
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=4000)])
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(current_app.config['ALLOWED_EXTENSIONS'], 'Images only!')
    ])
    captcha_token = HiddenField('Captcha Token')
    captcha_solution = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Create Thread')


class ReplyForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=4000)])
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(current_app.config['ALLOWED_EXTENSIONS'], 'Images only!')
    ])
    captcha_token = HiddenField('Captcha Token')
    captcha_solution = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Post Reply')


class BoardForm(FlaskForm):
    name = StringField('Board Name', validators=[DataRequired(), Length(max=64)])
    slug = StringField('Board Slug', validators=[DataRequired(), Length(max=64)])
    description = StringField('Description', validators=[Optional(), Length(max=256)])
    category = StringField('Category', validators=[DataRequired(), Length(max=64)])
    nsfw = BooleanField('NSFW')
    submit = SubmitField('Save Board')


class ModerateThreadForm(FlaskForm):
    sticky = BooleanField('Sticky')
    locked = BooleanField('Locked')
    delete = BooleanField('Delete')
    submit = SubmitField('Apply Changes')


class ModeratePostForm(FlaskForm):
    delete = BooleanField('Delete')
    submit = SubmitField('Apply Changes')
