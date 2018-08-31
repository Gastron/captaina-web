from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FieldList
import wtforms

class UsernamePasswordForm(FlaskForm):
    username = StringField('Username', validators=[wtforms.validators.DataRequired()])
    password = PasswordField('Password', validators=[wtforms.validators.DataRequired()])

class FeedbackForm(FlaskForm):
    message = TextAreaField('Message', 
            validators=[wtforms.validators.DataRequired(),
                wtforms.validators.Length(max=200000)],
            render_kw={"rows": 10, "cols":30})

class LessonCreatorForm(FlaskForm):
    title = StringField('Title', validators = [wtforms.validators.DataRequired()])
    raw_text = TextAreaField('Text to read', 
            validators=[wtforms.validators.DataRequired(),
                wtforms.validators.Length(max=200000)],
            render_kw={"rows": 10, "cols":30})


