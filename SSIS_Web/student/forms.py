from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField


class StudentForm(FlaskForm):
    pic = StringField('Student Picture')
    id = StringField('Student ID')
    firstName = StringField('First Name')
    lastName = StringField('Last Name')
    course = StringField('Course')
    year = IntegerField('Year')  # IntegerField for numeric input
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Non-binary', 'Non-binary'), ('Transgender',
                         'Transgender'), ('Prefer not to say', 'Prefer not to say'), ('Not listed', 'Not listed')])  # SelectField for dropdown input
    submit = SubmitField('Submit')  # Submit button field
