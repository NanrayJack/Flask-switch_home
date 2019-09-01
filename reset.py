import json
import os
from time import sleep

from sqlalchemy import create_engine

import secret
from app import configured_app
import config
from models.base_model import db
from models.topic.board import Board, BoardChoice
from models.topic.topic import Topic, compressd_img_path
from models.user import User
from models.topic.reply import Reply
from models.user_role import UserRoleEnum, UserRole
from static.fake_data.post_fake_data import fake_posts
from utils import map_board, map_user_role


def reset_database():
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(
        secret.database_password
    )
    e = create_engine(url, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS switch_home')
        c.execute('CREATE DATABASE switch_home CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE switch_home')

    db.metadata.create_all(bind=e)


def generate_fake_data():
    for ur in UserRoleEnum:
        form = dict(
            title=ur.name,
        )
        UserRole.new(form)

    dad = dict(
        username='dad',
        password='123',
        role=map_user_role[UserRoleEnum.parent.name],
        college='北京理工 ',
        valid_receive_mail=True,
        city='北京',
        email=config.test_mail,
        image='/static/fake_data/avatar/dad.jpg',
    )
    mom = dict(
        username='mom',
        password='123',
        role=map_user_role[UserRoleEnum.parent.name],
        college='南方科技大学',
        valid_receive_mail=True,
        city='深圳',
        email=config.test_mail,
        image='/static/fake_data/avatar/mom.jpg',
    )
    boy = dict(
        username='boy',
        password='123',
        role=map_user_role[UserRoleEnum.child.name],
        valid_receive_mail=True,
        college='四川大学',
        city='成都',
        email=config.test_mail,
        image='/static/fake_data/avatar/boy.jpg',
    )
    girl = dict(
        username='girl',
        password='123',
        role=map_user_role[UserRoleEnum.child.name],
        valid_receive_mail=True,
        college='上海交通大学',
        city='上海',
        email=config.test_mail,
        image='/static/fake_data/avatar/girl.jpg',
    )
    guest = dict(
        username='guest',
        password='123',
        role=map_user_role[UserRoleEnum.guest.name],
        valid_receive_mail=False,
        college='游客大学',
        city='游客城市',
    )
    User.register(guest)
    User.register(boy)
    User.register(girl)
    User.register(mom)
    User.register(dad)

    for b in BoardChoice:
        form = dict(
            title=b.name,
        )
        Board.new(form)

    with open("other_tools/jsons/college_tieba.json", 'r') as load_f:
        topics = json.load(load_f)
    u = User.one(username='boy')
    for t in topics:
        form = dict(
            title=t['title'],
            content=t['content'],
            board_id=map_board[BoardChoice.child_topic.name],
        )
        Topic.add(form, u.id)

    with open("other_tools/jsons/education_tieba.json", 'r') as load_f:
        topics = json.load(load_f)
    u = User.one(username='mom')
    for t in topics:
        form = dict(
            title=t['title'],
            content=t['content'],
            board_id=map_board[BoardChoice.parent_topic.name],
        )
        Topic.add(form, u.id)

    for root, dirs, files in os.walk('static/img/landscape'):
        fs = files
    # print(len(fs), fs)

    u = User.one(username='dad')

    times = 0
    for img_name in fs:
        times += 1
        if times == 10:
            break

        if 'out' in img_name:
            continue
        else:
            with open('markdown_demo.md', encoding='utf8') as f:
                content = f.read()
            original_cover_path = '/static/img/landscape/{}'.format(img_name)
            form = dict(
                title='post markdown demo',
                content=content,
                cover=original_cover_path,
                board_id=map_board[BoardChoice.post.name],
            )
            # TODO 已经存在的压缩图片重复压缩覆盖
            # [1:] 是去掉 /
            compressd_img_path(original_cover_path[1:])
            Topic.add(form, u.id)

    sleep(1)

    for p in fake_posts:
        form = dict(
            title=p['title'],
            content=p['content'],
            cover=p['cover'],
            board_id=map_board[BoardChoice.post.name],
        )
        # TODO 已经存在的压缩图片重复压缩覆盖
        # [1:] 是去掉 /
        compressd_img_path(p['cover'][1:])
        Topic.add(form, u.id)

    u = User.one(username='mom')
    for i in range(1, 11):
        form = dict(
            content='reply demo',
            topic_id=i,
        )
        Reply.add(form, u.id)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_data()
