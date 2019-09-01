import random
import time

from models.topic.board import BoardChoice
from models.user_role import UserRoleEnum


def log(*args, **kwargs):
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    format = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, flush=True, **kwargs)
        print(dt, *args, file=f, flush=True, **kwargs)
        # print(dt, *args, **kwargs)
        # print(dt, *args, file=f, **kwargs)


def random_string():
    secret_key = 'asdfkusdfcmnvoiwjnoinoipoerlmdsf'
    s = ''
    for i in range(50):
        c = secret_key[random.randint(0, len(secret_key)-1)]
        s += c
    return s


def not_in(topic, topics):
    for t in topics:
        if t.id == topic.id:
            return False
    return True


map_board = dict()
for i, b in enumerate(BoardChoice):
    map_board[b.name] = i + 1


map_user_role = dict()
for i, ur in enumerate(UserRoleEnum):
    map_user_role[ur.name] = i + 1


if __name__ == '__main__':
    print(map_board)
