from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, EmailField, BooleanField, ValidationError, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length
import datetime as dt

class Checkbox(FlaskForm):
    check = BooleanField()

# class Category(FlaskForm):
#     category = StringField(label="Name", validators=[DataRequired()])
#     submit = SubmitField(label="Add category")


class Todo(FlaskForm):
    name = StringField(label="Name", render_kw={"placeholder": "Enter task name..."}, validators=[DataRequired(message="Please actually enter a name"), Length(max=20, message="Please keep the name to 20 characters or less")])
    date_due = DateTimeLocalField(label="Date due", format="%Y-%m-%dT%H:%M", validators=[DataRequired(message="Please enter a time to complete the task by")])
    # category = SelectField(label="Category", choices=["Bills", "Dailies", "Other"], validators=[DataRequired(message="Please categorise this task")])
    notes = StringField(label="Notes", render_kw={"placeholder": "Enter notes (optional)..."}, validators=[Length(min=0, max=200)])
    submit_new_task = SubmitField(label="Add task")

    # https://stackoverflow.com/questions/56185306/how-to-validate-a-datefield-in-wtforms
    def validate_date_due(form, field):
        if field.data < dt.datetime.now(): #date_due=dt.datetime.strptime(request.form["date_due"], "%Y-%m-%d").date()
            raise ValidationError("Date due must not be before today")


class Login(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(message="You need to enter your email address"), Email(message="Invalid email address")])
    password = PasswordField(label="Password", validators=[DataRequired(message="You need to enter a password")])
    submit = SubmitField(label="Login")


class Register(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = EmailField(label="Email Address", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    repeat_pw = PasswordField(label="Repeat Password", validators=[DataRequired()])
    submit = SubmitField(label="Signup")

    def validate_repeat_pw(self, field):
        if self.password.data != field.data:
            raise ValidationError("Passwords do not match")
