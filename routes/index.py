import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort, current_app, Response)

from models.city import City
from models.college import College
from models.message import Messages
from models.topic.board import BoardChoice
from models.topic.topic import Topic
from models.user import User
from routes.helper import new_csrf_token, new_reset_password_token, cache, add_session, get_session, current_user
from routes.privilege_decorator import csrf_required, login_required
from utils import log, map_user_role, random_string

main = Blueprint('index', __name__)


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route('/')
def index():
    pts = Topic.latest_eight_by_board(board=BoardChoice.parent_topic.name)
    cts = Topic.latest_eight_by_board(board=BoardChoice.child_topic.name)
    ps = Topic.latest_eight_by_board(board=BoardChoice.post.name)
    log('pts, cts', len(pts), len(cts))
    u = current_user()
    cities = City.all()
    colleges = College.all()
    return render_template(
        "index.html",
        cities=cities,
        colleges=colleges,
        parent_topics=pts, child_topics=cts, posts=ps, user=u)


@main.route('/city/<int:id>')
def index_city(id):
    pts = Topic.latest_eight_by_board_mode_menu(id, menu='city', board=BoardChoice.parent_topic.name)
    cts = Topic.latest_eight_by_board_mode_menu(id, menu='city', board=BoardChoice.child_topic.name)
    ps = Topic.latest_eight_by_board_mode_menu(id, menu='city', board=BoardChoice.post.name)
    u = current_user()
    token = new_csrf_token()
    cities = City.all()
    colleges = College.all()
    return render_template(
        "index.html",
        token=token,
        cities=cities,
        colleges=colleges,
        parent_topics=pts, child_topics=cts, posts=ps, user=u)


@main.route('/college/<int:id>')
def index_college(id):
    pts = Topic.latest_eight_by_board_mode_menu(id, menu='college', board=BoardChoice.parent_topic.name)
    cts = Topic.latest_eight_by_board_mode_menu(id, menu='college', board=BoardChoice.child_topic.name)
    ps = Topic.latest_eight_by_board_mode_menu(id, menu='college', board=BoardChoice.post.name)
    u = current_user()
    token = new_csrf_token()
    cities = City.all()
    colleges = College.all()
    return render_template(
        "index.html",
        token=token,
        cities=cities,
        colleges=colleges,
        parent_topics=pts, child_topics=cts, posts=ps, user=u)


@main.route("/register/view")
def register_view():
    u = current_user()
    token = new_csrf_token()
    return render_template("register.html",
                           map_user_role=map_user_role,
                           token=token, user=u)


@main.route("/login/view")
def login_view():
    u = current_user()
    token = new_csrf_token()
    return render_template("login.html", token=token, user=u)


@main.route("/login", methods=['POST'])
@csrf_required
def login():
    form = request.form
    user = User.one(username=form['username'])
    u = User.validate_login(form)
    # print('login user <{}>'.format(u))
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        redirect_to_index = redirect(url_for('.index'))
        response = current_app.make_response(redirect_to_index)

        ran_str = random_string()
        session_id = add_session(ran_str, str(u.id))
        response.set_cookie('session_id', value=session_id)

        return response


@main.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session_id = request.cookies.get('session_id', default='')
    log('logout session_id <{}>'.format(session_id))
    if cache.exists(session_id):
        cache.delete(session_id)
        redirect_to_index = redirect(url_for('.index'))
        response: Response = current_app.make_response(redirect_to_index)
        response.delete_cookie('session_id')
        return response
    else:
        log('logout failed')
        return redirect(url_for('.index'))


@main.route("/password/to_reset/view")
def password_to_reset_view():
    u = User.guest()
    return render_template("password_to_reset_view.html", user=u)


@main.route("/password/reset/send", methods=['POST'])
@login_required
def reset_send():
    form = request.form.to_dict()
    u = User.one(username=form['username'])
    if u is None:
        abort(404)
    else:
        token = new_reset_password_token(u.id)
        Messages.send(
            title='{} 更改密码'.format(u.username),
            content='https://www.chenyehong.com/password/reset/view?token={}'.format(token),
            # 从 admin email 发到 user email, 现在只有一个
            sender_id=u.id,
            receiver_id=u.id
        )
    return redirect(url_for('.index'))


@main.route("/password/reset/view")
def password_reset_view():
    token = request.args['token']
    log('token', token)

    if cache.exists(token):
        return render_template(
            'password_reset_view.html',
            user=User.guest(),
            token=token,
        )
    else:
        abort(404)


@main.route("/password/reset", methods=['POST'])
def password_reset():
    form = request.form.to_dict()
    password = form['password']
    token = form['token']

    if cache.exists(token):
        user_id = int(cache.get(token).decode(encoding='utf-8'))
        cache.delete(token)
        password = User.salted_password(password)
        User.update(user_id, password=password)
        u = User.one(id=user_id)
        return redirect(url_for('index.index'))
    else:
        abort(404)


@main.route("/register", methods=['POST'])
@csrf_required
def register():
    # form = request.args
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        session_id = random_string()
        add_session(session_id, u.id)
        return redirect(url_for('.index'))


def not_found(e):
    return render_template('404.html')
