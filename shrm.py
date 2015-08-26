# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common import proxy, desired_capabilities
# from selenium.webdriver.firefox import webdriver
import requests


basic_url = 'http://www.shrm.org/communities/memberdirectory/pages/memdir.aspx'
second_url = 'http://apps.shrm.org/www/MemDir'
f = open('shrminfo.txt', 'w')
hdrs = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,it;q=0.2',
        'Cache-Control': 'max-age=0', 'Connection': 'keep-alive', 'Host': 'clicktale.pantherssl.com',
        'If-Modified-Since': 'Wed, 01 Jul 2015 06:21:21 GMT', 'If-None-Match': '"80c6a125c6b3d01:0"',
        'Referer': 'http://apps.shrm.org/www/MemDir/', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}

def login():
    # p = proxy.Proxy({
    #     'proxyType': proxy.ProxyType().MANUAL,
    #     'httpProxy': '127.0.0.1:3128'
    # })
    # capabilities = desired_capabilities.DesiredCapabilities().FIREFOX
    # p.add_to_capabilities(capabilities)
    # driver = webdriver.WebDriver(capabilities=capabilities)
    driver = webdriver.Firefox()
    driver.get(second_url)
    input_name = driver.find_element_by_name('ctl00$PlaceHolderMain$login1$login_id')
    input_pass = driver.find_element_by_name('ctl00$PlaceHolderMain$login1$login_password')
    input_name.send_keys('**')
    input_pass.send_keys('**')
    login = driver.find_element_by_id('ctl00_PlaceHolderMain_login1_login_submit')
    login.click()
    WebDriverWait(driver, 5)

    #     f.write(driver.page_source)

    # driver.get(second_url)
    city = driver.find_element_by_name('city')
    city.send_keys('New York')
    search = driver.find_element_by_xpath("//input[@value='Search Directory >']")
    search.click()

    patt = re.compile(r"([A-Z0-9]{8})")
    i = 0
    while i < 2:
    # while i < 157:
        for x in driver.find_elements_by_xpath("//a"):
            s = x.get_attribute('href')
            if 'memberDetails' in s:
                driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                driver.get('http://apps.shrm.org/www/MemDir/memberdetails.asp?id=' + re.search(patt, s).group(1))
                driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
        driver.find_elements_by_xpath("//a[@href]")[-1].click()
        i += 1


def parse_info():
    shrm = open('shrm.txt')
    for fs in shrm:
        print(fs)
        # hdrs['Referer'] = fs[:-1]
        # proxies = {'http': 'http://switchproxy.proxify.net:7491'}
        response = requests.get(fs[:-1])

        soup = BeautifulSoup(response.text)
        f.write(soup.find('table', bgcolor='#ffffff').text)
        f.write('-----------------------------------------')




if __name__ == '__main__':
    # login()
    parse_info()
    f.close()
    # search(second_url)
