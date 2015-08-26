# -*- coding: utf-8 -*-
import csv, requests, re, json, traceback, itertools, time, threading
from datetime import datetime
from bs4 import BeautifulSoup


hdrs = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,it;q=0.2',
        'Connection': 'keep-alive', 'Cookie': """vis=110e84575f9b1d17-063b421e71ed9544-216088a224082fc7v1; lang=en; _cb_ls=1; __ssid=25b386a1-ff95-4397-b571-df2f3c8d2a71; local_offset=-713; _ga=GA1.2.285379430.1434391134; _gat=1; mp_75b1d24a516ecfc955eadfadc4910661_mixpanel=%7B%22distinct_id%22%3A%20%22110e84575f9b1d17-063b421e71ed9544-216088a224082fc7v1%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.ru%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.ru%22%7D; _chartbeat2=rZ6VcDfhW5DTQJ4o.1434391134776.1436132589093.0111011111111111; last_page=https%3A%2F%2Fwww.kickstarter.com%2Fdiscover%2Fadvanced%3Fgoogle_chrome_workaround%26page%3D166%26category_id%3D1%26woe_id%3D0%26sort%3Dnewest; _ksr_session=Q21yRHFTQ0lLWk5DOThOb0lsTzFSZ0JJS1IxSG9zSm5zZkwwVENvdXduS0g4aWI2ZDdUSEE1K2RmU0dCdzNNRUF6VFdLUnF4QjEvYkE1ME9QbnFsMmlUNXQwd25NUm05TThZU0cybWtKVnFlTk5YcVlpLzdBL3c1cUU2RmE3R09OMW95WVVvZWJzNXFudWxtc0lScVg2Z0J3bWVKdEc1STZ4U1FqbkZVT1NUcnFVZDdGaTJzdXJkYTU4Sm9ac3M1NGpKK2JUSUJQYXBVZ0I2RTNBUmRlQT09LS0vMTRWbHk0Nm90Yis4ejNxQ1ZBVm5RPT0%3D--e23f65a58c8b9d2cf253359a06918fe2b9209ecd; request_time=Sun%2C+05+Jul+2015+21%3A47%3A28+-0000; _chartbeat5=545,2831,%2Fdiscover%2Fadvanced%3Fgoogle_chrome_workaround%26page%3D166%26category_id%3D1%26woe_id%3D0%26sort%3Dnewest,https%3A%2F%2Fwww.kickstarter.com%2Fdiscover%2Fadvanced%3Fgoogle_chrome_workaround%26page%3D166%26category_id%3D1%26woe_id%3D0%26sort%3Dnewest,CQcxx4ljeYBPvxXcrXFpSB1WUrt,*%5B%40id%3D'projects'%5D%2Fdiv%5B2%5D%2Fdiv%5B1%5D%2Fa%5B1%5D,c""",
        'Host': 'www.kickstarter.com', 'Referer': 'https://www.kickstarter.com/discover/advanced?google_chrome_workaround&page=166&category_id=1&woe_id=0&sort=newest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'X-CSRF-Token': 'Mw4tqfX1ObbOzz455dQMifKyK5cIAuaOurJCKFV1OlY=', 'X-Requested-With': 'XMLHttpRequest'}
start = time.time()
f = open('kickstarter.txt', 'w')
csvfile =  open('kickstarter.csv', 'w', encoding='utf-8')
writer = csv.writer(csvfile, lineterminator='\n')
writer.writerow(('Titel', 'Goal', 'Amount pledged', 'Is project funded (boolean)', 'Project category',
                 'Date launched', 'Will be funded', 'Amount of updates', 'Titel of update',
                 'Text of update', 'Amount of comments pr. update', 'Amount of likes pr. update', 'Dates of updates',
                 'Amount of project comments'))


def parse_part(url_f):
    response = requests.get(url_f, headers=hdrs)
    d = str(response.content, encoding='utf-8')
    j = json.loads(d)
    for x in j['projects']:
        url = x['urls']['web']['project']
        f.write(url + '\n')
        result = [[] for x in range(14)]
        result[-1] = comm_count(url)
        result[7:-1] = updates(url)
        launched = datetime.fromtimestamp(x['launched_at']).strftime("%a, %d %b %Y %H:%M:%S%Z GMT")
        be_funded = datetime.fromtimestamp(x['deadline']).strftime("%a, %d %b %Y %H:%M:%S%Z GMT")
        if x['pledged'] >= x['goal']: is_fund = str(True)
        else: is_fund = str(False)
        result[:7] = [x['name'], x['currency'] + ' ' + str(x['goal']), x['currency'] + ' ' + str(x['pledged']), is_fund,
                      x['category']['slug'], launched, be_funded]
        writer.writerow(result)


def updates_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    title_update = soup.find('h2', class_='normal title').text.strip()
    date = soup.find('p', class_='published h6 grey-dark').text
    try:
        content = soup.find('div', class_='body readability responsive-media formatted-lists').text.replace('\n', ' ').replace('\xa0', ' ').strip()
        comments = soup.find('div', class_='native-hide mobile-hide').text
    except AttributeError:
        content = 'For backers only.'
        comments = '0 Comments'
    return [title_update, content, comments, date]


def updates(url):
    no_updates = [[] for x in range(5)]
    url = url[:-20] + '/updates'
    response = requests.get(url, headers=hdrs)
    source = str(response.content, encoding='utf-8')
    soup = BeautifulSoup(source)
    upd_urls = []
    for x in soup.find_all('a', class_='grid-post link'):
        upd_urls.append('https://www.kickstarter.com' + x.get('href'))
    if len(upd_urls) > 0:
        for u in upd_urls:
            tmp = updates_content(u)
            no_updates[0].append(tmp[0])
            no_updates[1].append(tmp[1])
            no_updates[2].append(tmp[2])
            no_updates[-1].append(tmp[-1])
        for y in soup.find_all('div', class_='grid-post__metadata'):
            lks = y.text.strip()
            try:
                lks = lks.splitlines()[-1]
                if ('Comment' or 'For backers') in lks:
                    no_updates[-2].append('No likes')
                else:
                    no_updates[-2].append(lks)
            except IndexError:
                no_updates[-2].append('No likes')
        return [len(upd_urls)] + no_updates
    else:
        return ['No updates', 'No Title', 'No Text', 'No Comments', 'No Likes', 'No dates']


def comm_count(url):
    response = requests.get(url).text
    res = re.search('data-comments-count="(\d+)"', response)
    try:
        return str(res.group(1))
    except AttributeError:
        return '0'


def main_cont(d):
    threads = []
    # for x in range(26, 36):
    for x in range(4):
        url_f = 'https://www.kickstarter.com/discover/advanced?google_chrome_workaround&page=' + str(x) + ('&category_id=%d&woe_id=0&sort=newest' % d)
        f.write(url_f + '\n')
        thread = threading.Thread(target=parse_part, args=(url_f,))
        thread.start()
        threads.append(thread)
        print('Page: [[%s]] ID: [[%s]]' % (x, d))
        print('%.1f minutes' % ((time.time() - start) / 60))
    for t in threads: t.join()


if __name__ == '__main__':
    cat = (9, 10, 11, 12, 14, 1, 3, 6, 7, 13, 15, 16, 17, 18, 26)
    try:
        for x in cat: main_cont(x)
    except Exception as e:
        exc_f = open('kick_exc.txt', 'a')
        exc_f.write(traceback.format_exc() + '\n')
    # for i, x in enumerate(itertools.chain(range(25), range(56, 201))):
    # for k, v in d.items():
    #     for x in v:
    f.close()
    csvfile.close()
