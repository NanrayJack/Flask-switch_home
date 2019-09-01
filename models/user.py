import config
from sqlalchemy import Column, String, Integer, Boolean

from models.base_model import SQLMixin, db
from models.city import City, CityEnum
from models.college import College, CollegeEnum
from models.user_role import UserRoleEnum
from utils import map_user_role, log


def city_id_from_form(form):
    if 'city' not in form:
        city = ''
    else:
        city = form.pop('city')

    if city == '':
        m = City.one(title=CityEnum.unknown.name)
        if m is None:
            form = dict(
                title=CityEnum.unknown.name,
            )
            m = City.new(form)
    else:
        m = City.one(title=city)
        if m is None:
            form = dict(
                title=city,
            )
            m = City.new(form)
    return m.id


def college_id_from_form(form):
    if 'college' not in form:
        title = ''
    else:
        title = form.pop('college')

    if title == '':
        m = College.one(title=CollegeEnum.unknown.name)
        if m is None:
            form = dict(
                title=CollegeEnum.unknown.name,
            )
            m = College.new(form)
    else:
        m = College.one(title=title)
        if m is None:
            form = dict(
                title=title,
            )
            m = College.new(form)
    return m.id


class User(SQLMixin, db.Model):
    username = Column(String(50), nullable=False)
    password = Column(String(256), nullable=False)
    city_id = Column(Integer, nullable=True)
    college_id = Column(Integer, nullable=True)
    role = Column(Integer, nullable=True, default=1)
    image = Column(String(100), nullable=False, default='/static/fake_data/default_avatar.jpg')
    email = Column(String(50), nullable=True)
    valid_receive_mail = Column(Boolean, nullable=False, default=True)

    def city(self):
        return City.one(id=self.city_id).title

    def college(self):
        return College.one(id=self.college_id).title

    def role_name(self):
        for i, ur in enumerate(map_user_role):
            if i + 1 == self.role:
                return ur

    @classmethod
    def salted_password(cls, password, salt='$!@><?>HUI&DWQa`'):
        import hashlib
        def sha256(ascii_str):
            return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()
        hash1 = sha256(password)
        hash2 = sha256(hash1 + salt)
        print('sha256', len(hash2))
        return hash2

    def hashed_password(self, pwd):
        import hashlib
        # 用 ascii 编码转换成 bytes 对象
        p = pwd.encode('ascii')
        s = hashlib.sha256(p)
        # 返回摘要字符串
        return s.hexdigest()

    @classmethod
    def guest(cls):
        u = User.one(role=map_user_role[UserRoleEnum.guest.name])
        return u

    def is_guest(self):
        return self.role == map_user_role[UserRoleEnum.guest.name]

    @classmethod
    def register(cls, form):
        name = form['username']
        password = form['password']
        if len(name) > 2 and User.one(username=name) is None:
            form['city_id'] = city_id_from_form(form)
            form['college_id'] = college_id_from_form(form)
            u = User.new(form)
            u.password = u.salted_password(password)
            u.save()
            return u
        else:
            log('用户名长度小于 2 或用户名已存在')
            return None

    @classmethod
    def validate_login(cls, form):
        user = User.one(username=form['username'])
        print('validate_login <{}>'.format(form))
        if user is not None and user.password == User.salted_password(form['password']):
            return user
        else:
            return None


