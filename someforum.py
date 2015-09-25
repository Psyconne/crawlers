#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import datetime
from lxml import html
import MySQLdb

BASE_URL = 'http://forum.com/'
connect = MySQLdb.connect(host='localhost', user='user', passwd='psswrd', db='db')
connect.set_character_set('utf8')
cur = connect.cursor()
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')
LOG_FILENAME = 'log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


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
            yield BASE_URL + x.partition('&sid=')[0]


def get_posts(t):  # return a list of posts, where each post has the information described in Structure (above)
    all_posts = []

    def next_page_in_thread(url, append=False):
        thread_source = html.parse(url)
        if append:
            previous_thread = all_posts.pop()['posts']
        numerical_id = t.rpartition('.php?')[-1]
        thread = {'url': t, 'name': thread_source.xpath('//a[@class="maintitle"]')[0].text_content(), 'posts': [],
                  'numerical_id': numerical_id}
        member_names = []
        bodys = []
        urls = []
        for ts in thread_source.xpath('//span[@class="name"]'):
            member_names.append(ts.text_content())
        for i, ts in enumerate(thread_source.xpath('//tr//td[@colspan="2"]')[3:]):
            if i % 3 == 0:
                body = ''
                for s in ts.text_content().splitlines():
                    if s:
                        body += s + '\n'
                bodys.append(body)
        for x in thread_source.xpath('//td[@width="100%"]//a/@href'):
            if x.startswith('viewtopic.'):
                urls.append(BASE_URL + x)
        for name, body, url_post in zip(member_names, bodys, urls):
            post = {'member_name': name, 'body': body, 'post_id': numerical_id, 'post_url': url_post}
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


def save_mysql(thread):
    add_thread = ("INSERT INTO thread "
                  "(numerical_id, thread_name, thread_url) "
                  "VALUES (%s, %s, %s)")
    data_thread = (thread['numerical_id'], thread['name'], thread['url'])
    cur.execute(add_thread, data_thread)
    t_id = cur.lastrowid
    for p in thread['posts']:
        add_post = ("INSERT INTO post "
                    "(post_id, body, member_name, t_id, post_url) "
                    "VALUES (%s, %s, %s, %s, %s)")
        data_post = (p['post_id'], p['body'], p['member_name'], t_id, p['post_url'])
        cur.execute(add_post, data_post)
    connect.commit()


def get_new_threads():
    forum = get_forum()
    for f in forum:
        htm = html.parse(f)
        for topic in htm.xpath('//span[@class="topictitle"]//a/@href'):
            yield BASE_URL + topic.partition('&sid=')[0]


def check_and_save(url):
    # cur.execute("SELECT SUBSTRING_INDEX ('%s', '.php?t=', -1)" % url)
    cur.execute('SELECT thread_id FROM thread WHERE thread_url="%s"' % url)
    try:
        thread_from_db = cur.fetchone()[0]
        cur.execute('select id from post where t_id="%s"' % thread_from_db)
        old_posts = cur.fetchall()
        new_thread = next(get_posts(url))
        if len(old_posts) >= len(new_thread['posts']):
            pass
        else:
            start_index = len(old_posts)
            query = ("INSERT INTO post ""(t_id, post_id, member_name, body, post_url)" "VALUES (%s,%s,%s,%s,%s)")
            for post in new_thread['posts'][start_index:]:
                cur.execute(query, (thread_from_db, post['post_id'], post['member_name'], post['body'], post['post_url']))
            connect.commit()
            logging.debug('The new posts in the thread: %s' % url + '\n')
    except TypeError:
        logging.debug('The new thread has been added into MySQL Database: %s' % url + '\n')
        save_mysql(next(get_posts(url)))


if __name__ == "__main__":
    logging.debug(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S%Z GMT") + 
		' \n')
    logging.debug('Run insidepro.py' + '\n')
    new_threads = get_new_threads()
    for new_thread in new_threads:
        try:
            check_and_save(new_thread)
        except:
            logging.exception('Exception raised by MySQL.')
    # all_threads = get_threads()
    # for thread_url in all_threads:
    #     thread = next(get_posts(thread_url))
    #     save_mysql(thread)  # save all forum
    #     print("Thread name: %s" % thread['name'])
    #     print("Thread url: %s" % thread['url'])
    #     for post in thread['posts']:
    #         print("Post id: %s" % post['post_id'])
    #         print("Member name: %s" % post['member_name'])
    #         print("Post body: %s" % post['body'])
    cur.close()
    connect.close()
