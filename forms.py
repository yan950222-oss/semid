from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('author', 'Author'), ('editor', 'Editor')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此使用者名稱已存在')

class ManuscriptForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired(), Length(max=100)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save')
