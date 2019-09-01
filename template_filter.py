# @app.template_filter()
import time

from models.message import Messages
from utils import log


def count(input):
    log('count using jinja filter')
    return len(input)


def unchecked_message_num(user):
    messages = Messages.all(receiver_id=user.id, checked=False)
    return len(messages)


def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def summary(text):
    if len(text) > 50:
        return text[:48] + '...'
    return text


def topic_summary(text):
    max_length = 28
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text


def identity(role):
    map = dict(
        guest='游客',
        parent='父母',
        child='学生',
        unknown='未知',
    )
    return map.get(role, '未知')