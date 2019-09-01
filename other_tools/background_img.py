import json
import os
import time

import requests
from pyquery import PyQuery as pq


def get(url, filename):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'other_tools/cached'
    # 建立 cached 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
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


def cached_page(url):
    # filename = '{}.html'.format(url.split('=', 1)[-1])
    filename = 'bing-{}.html'.format(today())
    page = get(url, filename)
    return page


def remove_top_topic(divs):
    filtered_divs = []
    for d in divs:
        e = pq(d)
        if e('.icon-top').size() == 0:
            filtered_divs.append(d)
    return filtered_divs


def img_src_from_url(url):
    page = cached_page(url)
    e = pq(page)
    # print(e)
    items = e('#bgImgProgLoad')
    # print('items <{}>'.format(items))
    # print("items.attr('data-ultra-definition-src')", items.attr('data-ultra-definition-src'))
    return url + items.attr('data-ultra-definition-src')


def today():
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    format = '%Y-%m-%d'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    return dt


def save_img_src(src):
    folder = 'other_tools/jsons'
    # 建立 jsons 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open("other_tools/jsons/img_src.json", "r") as f:
        dict = json.load(f)

    date = today()
    if date not in dict:
        with open("other_tools/jsons/img_src.json", "r") as f:
            dict = json.load(f)
            dict[date] = src

        with open("other_tools/jsons/img_src.json", "w") as f:
            json.dump(dict, f, indent=4)


def main():
    url = 'https://cn.bing.com'
    img_src = img_src_from_url(url)
    save_img_src(img_src)
    return img_src


if __name__ == '__main__':
    main()
