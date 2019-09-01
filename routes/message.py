import json

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.user import User
from routes import *

from models.message import Messages
from routes.helper import current_user
from utils import log

main = Blueprint('mail', __name__)


@main.route('/')
def index():
    u = current_user()

    sent = Messages.all(sender_id=u.id)
    received = Messages.all(receiver_id=u.id)

    t = render_template(
        'mail/index.html',
        sent=sent,
        received=received,
        user=u,
    )
    return t


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    u = current_user()
    receiver_name = form['receiver_name']
    receiver_id = User.one(username=receiver_name).id
    # 发邮件
    Messages.send(
        title=form['title'],
        content=form['content'],
        sender_id=u.id,
        receiver_id=receiver_id
    )
    return redirect(url_for('.index'))


@main.route('/view/<int:id>')
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    # if u.id == mail.receiver_id or u.id == mail.sender_id:
    if u.id in [message.receiver_id, message.sender_id]:
        if u.id == message.receiver_id:
            message.check()
        res = dict(
            sender=message.sender().username,
            title=message.title,
            content=message.content,
        )
        # log('res', res)
        return json.dumps(res)
    else:
        return 'wrong'
