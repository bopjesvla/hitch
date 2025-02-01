from datetime import datetime

import pycountry
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import Optional
from wtforms.widgets import NumberInput


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [(None, "None")] + [(country.name, country.name) for country in pycountry.countries]


class UserEditForm(FlaskForm):
    gender = SelectField(
        "Gender",
        choices=[
            (None, "None"),
            ("Female", "Female"),
            ("Male", "Male"),
            ("Non-Binary", "Non-Binary"),
            ("Prefer not to say", "Prefer not to say"),
        ],
    )
    year_of_birth = IntegerField(
        "Year of Birth",
        widget=NumberInput(min=1900, max=datetime.now().year),
        validators=[Optional()],
    )
    hitchhiking_since = IntegerField(
        "Hitchhiking Since",
        widget=NumberInput(min=1900, max=datetime.now().year),
        validators=[Optional()],
    )
    origin_country = CountrySelectField("Where are you from?")
    origin_city = StringField("Which city are you from?", validators=[Optional()])
    hitchwiki_username = StringField("Hitchwiki Username", validators=[Optional()], default=None)
    trustroots_username = StringField("Trustroots Username", validators=[Optional()], default=None)
    submit = SubmitField("Submit")
