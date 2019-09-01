from flask import Flask
import secret
from models.base_model import db
from template_filter import (count,
                             summary,
                             format_time, identity, topic_summary, unchecked_message_num)
from utils import log

"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
from routes.profile import main as profile_routes
from routes.index import main as index_routes
from routes.topic.topic import main as topic_routes
from routes.topic.post import main as post_routes
from routes.topic.reply import main as reply_routes
from routes.message import main as mail_routes

from routes.utils_api import main as utils_api_routes
from routes.index import not_found

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# db = SQLAlchemy(app)


def remove_script(content):
    # log('remove_script <{}> '.format(content))
    # log('remove_script equal <{}> <{}> <{}>'.format(type(content), id(content[0]), id('<')))
    # content 在用了 | safe 过滤器后，不是 str 类型
    c = str(content)
    c = c.replace('>', '&gt;')
    c = c.replace('<', '&lt;')
    c = c.replace('script', 'removed')
    print('remove_script after <{}>'.format(c))
    return c


def configured_app():
    app = Flask(__name__)
    # # 设置 secret_key 来使用 flask 自带的 session
    # # 这个字符串随便你设置什么内容都可以
    # app.secret_key = config.secret_key
    # 数据返回顺序
    # mysql -> pymysql -> sqlalchemy -> route
    # 初始化顺序
    # app -> flask-sqlalchemy -> sqlalchemy -> pymysql -> mysql

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/switch_home?charset=utf8mb4'.format(
        secret.database_password
    )
    db.init_app(app)

    app.register_blueprint(index_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(post_routes, url_prefix='/post')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(mail_routes, url_prefix='/message')
    app.register_blueprint(utils_api_routes)
    log('url map', app.url_map)

    # @app.template_filter()
    # def count(input):
    # app.template
    app.template_filter()(count)
    app.template_filter()(format_time)
    app.template_filter()(summary)
    app.template_filter()(topic_summary)
    app.template_filter()(identity)
    app.template_filter()(remove_script)
    app.template_filter()(unchecked_message_num)

    app.errorhandler(404)(not_found)
    return app


# 运行代码
if __name__ == '__main__':
    app = configured_app()
    # app.add_template_filter(count)
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    # 自动 reload jinja
    #
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=3000,
    )
    app.run(**config)
