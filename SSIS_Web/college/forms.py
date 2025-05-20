from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField

class CollegeForm(FlaskForm):
    id = StringField('Code')
    firstname = StringField('Name')
    submit = SubmitField('Submit')  # Submit button field