from enum import (
    Enum,
    auto,
)

from sqlalchemy import Column, Unicode
from models.base_model import SQLMixin, db


class UserRole(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)


class UserRoleEnum(Enum):
    parent = auto()
    child = auto()
    guest = auto()
    unknown = auto()

    # # 让 mysql 支持枚举, BoardChoice.post 在 pymysql 可隐式自动转换为 string
    # # 现在不需要用上, 用 BoardChoice.post.name 即可转为 str
    # def translate(self, _escape_table):
    #     return self.name
