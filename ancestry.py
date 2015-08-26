# -*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
import json
import xlsxwriter
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotVisibleException

driver = None


def login():
    driver = webdriver.Firefox()
    driver.get('http://turing.library.northwestern.edu/login?url=http://ancestrylibrary.proquest.com')
    input_name = driver.find_element_by_name('IDToken1')
    input_pass = driver.find_element_by_name('IDToken2')
    input_name.send_keys('*****')
    input_pass.send_keys('********')
    login = driver.find_element_by_name('Login.Submit')
    login.click()
    return driver


def parse(url):
    driver.get(url)
    try:
        decline = driver.find_element_by_xpath('//a[@class="fsrDeclineButton"]')
        decline.click()
    except NoSuchElementException:
        pass
    wait = WebDriverWait(driver, 10)
    dropdown = driver.find_element_by_xpath("//select[@name='hc']/option[text()='50']").click()
    # next_page = driver.find_element_by_xpath('//li[@class="next"]//a')
    while True:
        WebDriverWait(driver, 5)
        urls = wait.until(lambda driver: driver.find_elements_by_xpath('//table//tr[@valign="top"]'))
        for x in urls:
            f.write('http://search.ancestrylibrary.com' + x.get_attribute('jsopen') + '\n')
        WebDriverWait(driver, 5)
        try:
            next_page = wait.until(lambda driver : driver.find_element_by_xpath('//li[@class="next"]//a'))
            next_page.click()
        except TimeoutException:
            pass
            break
        except ElementNotVisibleException or IndexError:
            decline = driver.find_element_by_xpath('//a[@class="fsrDeclineButton"]')
            decline.click()
            next_page = wait.until(lambda driver : driver.find_element_by_xpath('//li[@class="next"]//a'))
            next_page.click()


def parse_detail(url):
    driver.get(url)
    res = {'Name': '', 'Departure Date': '', 'Destination': '', 'Birth Date': '', 'Age': '', 'Gender': '', 'Residence': '',
           'Occupation': '','Ship Name': '','Captain': '','Shipping Clerk': '','Ship Type': '','Accommodation': '',
           'Ship Flag': '','Port of Departure': '','Port of Arrival': '','Volume': '','Household Members': '',
           'Relationship': '', 'Ethnicity/Nationality': '', 'Marital Status': ''}
    for x in driver.find_elements_by_xpath('//table[@class="table tableHorizontal tableHorizontalRuled"]//tr')[:-1]:
        if not (x.text.split(':') == [' ']):
            if 'Household Members' in x.text.split(':'):
                res['Household Members'] = []
                break
            try:
                res[x.text.split(':')[0]] = x.text.split(':')[1].strip()
            except IndexError:
                decline = driver.find_element_by_xpath('//a[@class="fsrDeclineButton"]')
                decline.click()
                res[x.text.split(':')[0]] = x.text.split(':')[1].strip()
    for x in driver.find_elements_by_xpath('//table[@class="p_embedTable table"]//tr')[1:]:
        res['Household Members'].append(x.text)
    return res


def load_json(filename):
    with open(filename) as j_f:
        j = json.load(j_f)
    return j


def xlsx(jsn, xlsxfile):
    workbook = xlsxwriter.Workbook(xlsxfile)
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(20)
    worksheet.set_column('A:A', 15)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Name', bold)
    row = 1
    col = 0
    for res in jsn:
        worksheet.write(row, col+0, res['Name'])
        hhm = ''
        for x in res['Household Members']:
            hhm += x + '\n'
        worksheet.write(row, col+19, hhm)
        if not res['Relationship']:
            worksheet.write(row, col+20, 'Empty')
        worksheet.write(row, col+20, res['Relationship'])
        row += 1
    workbook.close()


if __name__ == '__main__':
    driver = login()
    for x in range(1883, 1914):
        url = 'http://search.ancestrylibrary.com/cgi-bin/sse.dll?db=HamburgPL_full&gss=sfs28_ms_r_db&new=1&rank=1&msrpn__ftp=Romania&msrpn=5188&msrpn_PInfo=3-%7C0%7C1652381%7C0%7C5188%7C0%7C0%7C0%7C0%7C0%7C0%7C&msedy=' + str(x) + '&msedy_x=1&_83004003-n_xcl=f'
        json_name = str(x) + '_.json'
        text_name = str(x) + '_.txt'
        xlsx_name = str(x) + '_.xlsx'
        with open(text_name, 'w', encoding='utf-8') as f:
            parse(url)
        with open(text_name) as f:
            with open(json_name, 'w', encoding='utf-8') as json_file:
                json_file.write("[")
                for url in f:
                    r = parse_detail(url[:-1])
                    line = json.dumps(dict(r)) + ",\n"
                    json_file.write(line)
    # xlsx(load_json('1910_.json'), '1910_.xlsx') # call this function only when code above is completed.
