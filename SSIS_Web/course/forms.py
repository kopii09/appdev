from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField

class CourseForm(FlaskForm):
    id = StringField('Code')
    firstName = StringField('Name')
    lastName = StringField('College')
    submit = SubmitField('Submit')  # Submit button field