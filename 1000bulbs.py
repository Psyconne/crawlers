from bs4 import BeautifulSoup
import requests
import csv
import re
import xlsxwriter

main_url = 'https://www.1000bulbs.com/category/led-light-bulbs/'
url = 'https://www.1000bulbs.com/category/led-r30-flood-lights/'
final_list = []


def parse(url):
    print(url)
    res = dict(zip(['Brand:', 'Family:', 'Part No.:', 'Title', 'Sub Title', 'Description', 'UPC:', 'Wattage:',
                    'Voltage:', 'Bulb Shape:', 'Base Type:', 'Dimmable:', 'Color:', 'Color Temperature:', 'CRI:',
                    'Length:','Diameter:','Energy Star:','Incandescent Equal:','Life Hours:','Light Source:',
                    'Lumens (Initial):','Lumens Per Watt:','UL Listed:','Warranty:','Case Quantity:','Picture 1',
                    'Picture 2','Spec Sheet', 'Broshure', 'Warranty', 'Dimmer Compatibility'], [' ' for x in range(32)]))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    title = soup.find('h1', class_='primary-color smaller').text
    subtitle = soup.find('h2', class_="smaller").text
    desc = soup.find('div', class_='small-12 medium-8 columns description').text
    pictures = []
    try:
        picture = soup.find('div', class_='columns medium-5 large-push-1 small-12').find_all('div')[1]
        for p in picture.find_all('img'):
            pictures.append(p.get('src'))
    except AttributeError:
        pictures = 'No picture'
    if len(pictures) == 1:
        res['Picture 1'] = pictures[0]
    else:
        res['Picture 1'], res['Picture 2'] = pictures[0], pictures[1:]
    for s in soup.find_all('div', class_='columns small-12 medium-6'):
        try:
            for a in s.find_all('a'):
                pdf = a.get('href')
                if pdf.endswith('-specs.pdf'):
                    res['Spec Sheet'] = 'https://www.1000bulbs.com' + pdf
                elif pdf.endswith('-brochure.pdf'):
                    res['Broshure'] = 'https://www.1000bulbs.com' + pdf
                elif pdf.endswith('-warranty.pdf'):
                    res['Warranty'] = 'https://www.1000bulbs.com' + pdf
                elif pdf.endswith('-dimmers.pdf'):
                    res['Dimmer Compatibility'] = 'https://www.1000bulbs.com' + pdf
        except AttributeError:
            pass
    res['Title'] = title
    res['Description'] = desc.strip()
    res['Picture'] = picture
    res['Sub Title'] = subtitle
    # for x in soup.find_all('td', class_='right'):
    #     print(x.text)
    x = soup.find_all('table')
    result = []
    for t in x[-1].find_all('td'):
        result.append(t.text)
    try:
        for t in (x[-2]).find_all('td'):
            result.append(t.text)
    except IndexError:
        pass
    i = 0
    for r in range(len(result) // 2):
        res[result[i]] = result[i+1]
        i += 2
    # for k, v in res.items():
    #     print(k, v, sep=' ==>> ')
    # print(list(res.values()))
    # final_list.append(res)
    final_list.append([res['Brand:'], res['Family:'], res['Part No.:'], res['Title'], res['Sub Title'], res['Description'],
            res['UPC:'], res['Wattage:'], res['Voltage:'], res['Bulb Shape:'], res['Base Type:'], res['Dimmable:'],
            res['Color:'], res['Color Temperature:'], res['CRI:'], res['Length:'], res['Diameter:'], res['Energy Star:'],
            res['Incandescent Equal:'], res['Life Hours:'], res['Light Source:'], res['Lumens (Initial):'],
            res['Lumens Per Watt:'], res['UL Listed:'], res['Warranty:'], res['Case Quantity:'], res['Picture 1'],
            res['Picture 2'], res['Spec Sheet'], res['Broshure'], res['Warranty'], res['Dimmer Compatibility']])


def save(x_file):
    workbook = xlsxwriter.Workbook('1000bulbs.xlsx', {'strings_to_urls': False})
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(20)
    worksheet.set_column('A:A', 40)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Manufacturer', bold)
    row = 2
    col = 0
    for x in range(len(x_file)):
        for y in range(32):
            worksheet.write(row, col+y, ''.join(x_file[x][y]))
        row += 1
    workbook.close()


def third_level(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    if len(soup.find_all('h4')) == 1:
        second_level(url)
    else:
        for s in soup.find_all('h4'):
            if s.find('a') is not None:
                parse('https://www.1000bulbs.com' + s.find('a').get('href'))



def second_level(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    for x in soup.find_all('li', class_="text-center"):
        if x.find('a').get('href'):
            third_level('https://www.1000bulbs.com' + x.find('a').get('href'))

def first_level(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    s = soup.find('ul', class_='small-block-grid-2 medium-block-grid-4')
    res = {}
    for x in s.find_all('a'):
        if x.get('href').startswith('/category'):
            res['https://www.1000bulbs.com' + x.get('href')] = 1
    for k in res:
        second_level(k)

if __name__ == '__main__':
    first_level(main_url)
    save(final_list)
