import os

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort, jsonify, session)

import config
from models.user import User
from other_tools import background_img

from utils import log

main = Blueprint('utils_api', __name__)


@main.route('/get_background_src')
def get_background_img_src():
    img_src = background_img.main()
    return img_src