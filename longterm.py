# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import xlsxwriter
import xlrd

# url = 'https://www.longtermcarelink.net/a8profiles.htm'
# response = requests.get(url)
# source = response.text
# soup = BeautifulSoup(source)
# big_one = []
# for x in soup.find_all('strong'):
#     y = x.find('a').text
#     x = 'https://www.longtermcarelink.net/' + x.find('a').get('href')
#     data = get_data(x)
#     big_one.append(data.insert(0, y))

big_one = []


def get_data(url, cat):
    rspns = requests.get(url)
    src = rspns.text
    soup = BeautifulSoup(src)
    detect = 'Pioneer First Alert provides FREE equipment and FREE installation.'
    for x in soup.find_all('td'):
        if x.find('span') and detect not in x.text:
            try:
                link = 'https://www.longtermcarelink.net/' + x.find('a').get('href')
            except AttributeError:
                link = 'No link'
            text = x.text.split('\n')
            areas = text[0].strip()
            name = text[1].strip()
            try:
                zip = x.text.split('\n')[2].split()[-1]
                street = text[2].strip()
            except IndexError:
                street = text[-2].strip()
                zip = street.split()[-1]
            state = street.split()[-2]
            try:
                city = street.split()[-3]
            except IndexError:
                city = street.split()[-2]
            indx = street.index(city) - 1
            street = street[:indx]
            big_one.append([cat, areas, name, street, city, state, zip, link])


def save(args):
    print('%d results found' % len(args))
    workbook = xlsxwriter.Workbook('longtermcarelink.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(30)
    worksheet.set_column('A:A', 40)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:D', 40)
    worksheet.set_column('H:H', 40)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Category', bold)
    worksheet.write('B1', 'Areas', bold)
    worksheet.write('C1', 'Name', bold)
    worksheet.write('D1', 'Street', bold)
    worksheet.write('E1', 'City', bold)
    worksheet.write('F1', 'State', bold)
    worksheet.write('G1', 'Zip', bold)
    worksheet.write('H1', 'Link', bold)
    ldwntwrk = "The ElderLaw Network"
    row = 1
    col = 0
    for x in range(len(args)):
        for y in range(8):
            worksheet.write(row, col+y, ''.join(args[x][y]))
        row += 1
    workbook.close()


def main():
    global url, response, source, soup, x, y, data
    url = 'https://www.longtermcarelink.net/a8profiles.htm'
    response = requests.get(url)
    source = response.text
    soup = BeautifulSoup(source)
    for x in soup.find_all('strong'):
        y = x.find('a').text
        x = 'https://www.longtermcarelink.net/' + x.find('a').get('href')
        get_data(x, y)
    save(big_one)

main()

# def find_city(s):
#     patt = re.compile(r'(\d+)(\D+)(\D+)(\D+)(\d{5})$')
#     m = re.search(patt,s)
#     city = m.group(2)

# print(get_data('https://www.longtermcarelink.net/a7homecare.htm', 'atr'))
