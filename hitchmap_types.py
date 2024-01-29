from pydantic import BaseModel, conint, constr, confloat, field_validator
from typing import Optional
import re
import requests

MIN_RATING = 1
MAX_RATING = 5
MAX_COMMENT_LENGTH = 10000
NATURAL_NUM = conint(ge=0)
UNKNOWN = "unknown"
HITCH_SPOT_INDEX = 'id'

class HitchhikeSpot(BaseModel):
    id: NATURAL_NUM
    rating: conint(ge=MIN_RATING, le=MAX_RATING)
    wait: Optional[NATURAL_NUM]
    comment: Optional[constr(max_length=MAX_COMMENT_LENGTH)]
    name: Optional[str]
    datetime: str
    ip: str
    reviewed: bool = False
    banned: bool = False
    lat: confloat(ge=-90, le=90)
    dest_lat: confloat(ge=-90, le=90)
    lon: confloat(ge=-180, le=180)
    dest_lon: confloat(ge=-180, le=180)
    country: str

    @field_validator("wait", mode="before")
    def wait_validator(cls, wait):
        return (int(wait) if wait != '' else None)

    @field_validator("comment", mode="before")
    def comment_validator(cls, comment):
        return (None if comment == '' else comment)

    @field_validator("name", mode="before")
    def name_validator(cls, name):
        return (name if re.match(r'^\w{1,32}$', name) else None)

    @field_validator("country", mode="before")
    def country_validator(cls, coords):
        res = requests.get('https://nominatim.openstreetmap.org/reverse',
                           {'lat': coords[0], 'lon': coords[1], 'format': 'json', 'zoom': 3}).json()
        return UNKNOWN if 'error' in res else res['address']['country_code'].upper()