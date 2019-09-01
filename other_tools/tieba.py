import json
import os
import requests
from pyquery import PyQuery as pq

"""
这是一个普通爬虫
下载网页并解析打印出来
但是只下载了一个网页
"""


class Model():
    """
    基类, 用来显示类的信息
    """
    def __repr__(self):
        name = self.__class__.__name__
        properties = ['{}=({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Topic(Model):
    """
    存储电影信息
    """
    def __init__(self):
        self.title = ''
        self.content = 0
        self.author = ''
        self.last_replier = ''
        # self.replies = []
        # self.cover_url = ''
        # self.ranking = 0


def get(url, filename):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    # 建立 cached 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, '{}.html'.format(filename))
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def topic_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    # print('topic_from_div', type(div), div)
    e = pq(div)

    # 小作用域变量用单字符
    m = Topic()
    m.title = e('.j_th_tit ').text()
    m.content = e('.threadlist_abs.threadlist_abs_onlyline').text()
    # print('m.content', m.content)
    author_and_last = e('.frs-author-name.j_user_card').text().split(' ')
    if len(author_and_last) > 1:
        m.author, m.last_replier = author_and_last
    else:
        m.author = author_and_last
    # print(m.author, m.last_replier)
    # m.quote = e('.inq').text()
    # m.cover_url = e('img').attr('src')
    # m.ranking = e('.pic em').text()
    # for e in find_all(class='pic'):
    #   find_by(e, 'em')
    return m


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        get(m.cover_url, filename)


def cached_page(url, filename):
    # filename = '{}.html'.format(url.split('=', 1)[-1])
    page = get(url, filename)
    return page


def remove_top_topic(divs):
    filtered_divs = []
    for d in divs:
        e = pq(d)
        if e('.icon-top').size() == 0:
            filtered_divs.append(d)
    return filtered_divs


def topics_from_url(url, filename):
    """
    从 url 中下载网页并解析出页面内所有的帖子
    """
    page = cached_page(url, filename)
    e = pq(page)
    items = e('.j_thread_list')
    items = remove_top_topic(items)
    # __iter__ 迭代器
    topics = [topic_from_div(i) for i in items]
    return topics


def save_json(models, filename):
    folder = 'jsons'
    # 建立 jsons 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)
    dicts = [m.__dict__ for m in models]
    with open("jsons/{}.json".format(filename), "w") as f:
        json.dump(dicts, f, indent=4)


def save_topics(url, filename):
    topics = topics_from_url(url, filename)
    save_json(topics, filename)


def main():
    filename = 'education_tieba'
    url = 'http://tieba.baidu.com/f?ie=utf-8&kw=%E6%95%99%E8%82%B2&fr=search&red_tag=b0440876379'
    save_topics(url, filename)

    filename = 'college_tieba'
    url = 'http://tieba.baidu.com/f?ie=utf-8&kw=%E5%A4%A7%E5%AD%A6&fr=search'
    save_topics(url, filename)


if __name__ == '__main__':
    main()
