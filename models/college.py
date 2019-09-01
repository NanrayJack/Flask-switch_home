from enum import Enum, auto

from sqlalchemy import Column, Unicode
from models.base_model import SQLMixin, db


class College(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)


class CollegeEnum(Enum):
    unknown = auto()
