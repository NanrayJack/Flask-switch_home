from enum import Enum, auto

from sqlalchemy import Column, Unicode
from models.base_model import SQLMixin, db


class City(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)


class CityEnum(Enum):
    unknown = auto()
