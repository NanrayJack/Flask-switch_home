from time import sleep

from marrow.mailer import Mailer
from sqlalchemy import Column, Unicode, UnicodeText, Integer, Boolean

from config import admin_mail
import secret
from models.base_model import SQLMixin, db
from models.user import User
from tasks import send_async_simple, send_async
from utils import log
import threading


def configured_mailer():
    config = {
        # 'manager.use': 'futures',
        'transport.debug': True,
        # 'transport.timeout': 1,
        'transport.use': 'smtp',
        'transport.host': 'smtp.exmail.qq.com',
        'transport.port': 465,
        'transport.tls': 'ssl',
        'transport.username': admin_mail,
        'transport.password': secret.mail_password,
    }
    m = Mailer(config)
    m.start()
    return m


mailer = configured_mailer()


def send_mail(subject, author, to, content):
    # 延迟测试
    # sleep(30)
    m = mailer.new(
        subject=subject,
        author=author,
        to=to,
    )
    m.plain = content

    # log('subject <{}>'.format(subject))
    # log('author <{}>'.format(author))
    # log('to <{}>'.format(to))
    # log('content <{}>'.format( content))

    mailer.send(m)


class Messages(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    checked = Column(Boolean, nullable=False, default=False)

    def sender(self):
        u = User.one(id=self.sender_id)
        return u

    def receiver(self):
        u = User.one(id=self.receiver_id)
        return u

    def check(self):
        Messages.update(self.id, checked=True)

    @staticmethod
    def send(title: str, content: str, sender_id: int, receiver_id: int):
        form = dict(
            title=title,
            content=content,
            sender_id=sender_id,
            receiver_id=receiver_id
        )
        log('send form', form)
        Messages.new(form)
        receiver: User = User.one(id=receiver_id)

        if receiver.valid_receive_mail:
            send_async_simple.delay(
                subject=form['title'],
                author=admin_mail,
                to=receiver.email,
                plain=form['content']
            )
