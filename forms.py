from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FieldList, FormField, Label, EmailField, \
    DateField, IntegerField, TextAreaField, BooleanField, TimeField
from wtforms.validators import InputRequired, Length, Email, NumberRange, ValidationError, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField('Login')


class EditSingleSessionForm(FlaskForm):
    delete_client = BooleanField("Очистити клієнта:")
    add_client = SelectField("Додати клієнта", default="Нікого")
    status = SelectField("Статус")
    submit = SubmitField('Зберегти')


class DeleteClient(FlaskForm):
    delete_client = BooleanField("Очистити клієнта:")


class EditGroupSessionForm(FlaskForm):
    status = SelectField("Статус")
    change_coach = SelectField("Змінити коуча")
    date = DateField("Задати нову дату")
    starting_time = TimeField("Змінити час початку")
    delete_client = SelectField("Видалити клієнта", default="Нікого")

    submit = SubmitField('Зберегти')
