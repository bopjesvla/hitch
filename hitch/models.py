from datetime import datetime

import pycountry
from flask_security.models import fsqla_v3 as fsqla
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import Optional
from wtforms.widgets import NumberInput

from hitch.extensions import db

fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    gender = db.Column(db.String(255), default=None)
    year_of_birth = db.Column(db.Integer, default=None)
    hitchhiking_since = db.Column(db.Integer, default=None)
    origin_country = db.Column(db.String(255), default=None)
    origin_city = db.Column(db.String(255), default=None)
    hitchwiki_username = db.Column(db.String(255), default=None)
    trustroots_username = db.Column(db.String(255), default=None)


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(None, "None")] + [
            (country.name, country.name) for country in pycountry.countries
        ]


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
    hitchwiki_username = StringField(
        "Hitchwiki Username", validators=[Optional()], default=None
    )
    trustroots_username = StringField(
        "Trustroots Username", validators=[Optional()], default=None
    )
    submit = SubmitField("Submit")
