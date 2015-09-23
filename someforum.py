#!/usr/bin/python3
# -*- coding: utf-8 -*-
from lxml import html
import MySQLdb

BASE_URL = 'www.example.com'
connect = MySQLdb.connect(host='localhost', user='user', passwd='psswd', db='db')
connect.set_character_set('utf8')
cur = connect.cursor()
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')


def get_forum():
    h = html.parse(BASE_URL)
    for x in h.xpath('//span[@class="forumlink"]//a/@href'):
        yield BASE_URL + x


def get_threads():  # return a list of threads, where each thread has the information described in Structure (above)
    forum = get_forum()
    for f in forum:
        all_urls = []

        def next_page(url):
            ht = html.parse(url)
            for x in ht.xpath('//span[@class="topictitle"]//a/@href'):
                if x not in all_urls:
                    all_urls.append(x)
            next_p = ht.xpath('//span[@class="nav"]//a')[-1]
            if next_p.text_content() == 'Next':
                url = BASE_URL + next_p.get('href')
                next_page(url)
        next_page(f)
        for x in all_urls:
            yield BASE_URL + x


def get_posts():  # return a list of posts, where each post has the information described in Structure (above)
    all_threads = get_threads()
    for t in all_threads:
        t = t.partition('&sid=')[0]
        all_posts = []

        def next_page_in_thread(url, append=False):
            thread_source = html.parse(url)
            print(t)
            if append:
                previous_thread = all_posts.pop()['posts']
            thread = {'url': t, 'name': thread_source.xpath('//a[@class="maintitle"]')[0].text_content(), 'posts': []}
            member_names = []
            bodys = []
            for ts in thread_source.xpath('//span[@class="name"]'):
                member_names.append(ts.text_content())
            for i, ts in enumerate(thread_source.xpath('//tr//td[@colspan="2"]')[3:]):
                if i % 3 == 0:
                    body = ''
                    for s in ts.text_content().splitlines():
                        if s:
                            body += s + '\n'
                    bodys.append(body)
            for name, body in zip(member_names, bodys):
                post = {'member_name': name, 'body': body, 'post_id': t.partition('?t=')[-1]}
                thread['posts'].append(post)
            if append:
                thread['posts'] = previous_thread + thread['posts']
            all_posts.append(thread)
            next_p = thread_source.xpath('//span[@class="nav"]//a')[-1]
            if next_p.text_content() == 'Next':
                url = BASE_URL + next_p.get('href')
                next_page_in_thread(url, append=True)
        next_page_in_thread(t, append=False)
        yield from all_posts


def save_mysql():
    threads = get_posts()
    for thread in threads:
        add_thread = ("INSERT INTO thread "
                   "(thread_name, thread_url) "
                   "VALUES (%s, %s)")
        data_thread = (thread['name'], thread['url'])
        cur.execute(add_thread, data_thread)
        t_id = cur.lastrowid
        for p in thread['posts']:
            add_post = ("INSERT INTO post "
                       "(post_id, body, member_name, t_id) "
                       "VALUES (%s, %s, %s, %s)")
            data_post = (p['post_id'], p['body'], p['member_name'], t_id)
            cur.execute(add_post, data_post)
    connect.commit()


if __name__ == "__main__":
    save_mysql()
    # threads = get_posts()
    # for thread in threads:
    #     print("Thread name: %s" % thread['name'])
    #     print("Thread url: %s" % thread['url'])
    #     for post in thread['posts']:
    #         print("Post id: %s" % post['post_id'])
    #         print("Member name: %s" % post['member_name'])
    #         print("Post body: %s" % post['body'])
    cur.close()
    connect.close()
