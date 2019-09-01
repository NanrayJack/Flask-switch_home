import json
import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort)
from werkzeug.datastructures import FileStorage

from models.topic.topic import Topic
from models.user import User, city_id_from_form, college_id_from_form
from routes.helper import new_csrf_token, current_user, cache
from routes.privilege_decorator import csrf_required, login_required

from utils import log, map_user_role

main = Blueprint('profile', __name__)


def _replied_topics(user_id):
    k = 'replied_topics_{}'.format(user_id)
    if cache.exists(k):
        v = cache.get(k)
        ts = json.loads(v)
        res = [Topic.construct(t) for t in ts]
    else:
        res = Topic.participate_topics(user_id)
        v = json.dumps([t.json() for t in res])
        cache.set(k, v)
    return res


@main.route('/profile')
def profile():
    u = current_user()
    # if u.is_guest():
    #     return redirect(url_for('index.login_view'))
    # else:
    created_topics = Topic.created_topics(user_id=u.id)
    replied_topics = _replied_topics(u.id)
    log('replied_topics len <{}> <{}>'.format(len(replied_topics), type(replied_topics)))
    return render_template(
        'profile/profile.html',
        user=u,
        created_topics=created_topics,
        replied_topics=replied_topics,
    )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        created_topics = Topic.created_topics(user_id=u.id)
        replied_topics = _replied_topics(u.id)
        log('replied_topics len <{}> <{}>'.format(len(replied_topics), type(replied_topics)))
        # log('replied_topics', replied_topics)
        return render_template(
            'profile/profile.html',
            user=u,
            created_topics=created_topics,
            replied_topics=replied_topics,
        )


@main.route('/profile/edit')
@login_required
def profile_edit():
    u = current_user()
    token = new_csrf_token()
    return render_template(
        'profile/edit.html',
        map_user_role=map_user_role,
        token=token, user=u)


@main.route('/profile/update', methods=["POST"])
@csrf_required
def update():
    form = request.form.to_dict()
    form['city_id'] = city_id_from_form(form)
    form['college_id'] = college_id_from_form(form)

    user_id = form.pop('user_id')
    log('DEBUG', form)
    User.update(user_id, **form)
    token = new_csrf_token()
    return redirect(url_for('.profile', token=token))


@main.route('/image/add', methods=['POST'])
# @csrf_required
def avatar_add():
    log('avatar_add')
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # upload_images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('static/upload_images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/static/upload_images/{}'.format(filename))

        token = new_csrf_token()
        return redirect(url_for('.profile_edit', token=token))
