# -*- coding: utf-8 -*-
import xlsxwriter
import requests
from bs4 import BeautifulSoup

big_one = []

def get_data(url):
    print(url)
    response = requests.get(url)
    src = response.text
    soup = BeautifulSoup(src)
    name = r'Organization Name:'
    for x in soup.find_all('table'):
            spisok = x.text.split('\n\n')
            if name in spisok[1]:
                clear_data(spisok)


def clear_data(org):
    res = ['Empty' for x in range(11)]
    while True:
        if '' in org:
            del org[org.index('')]
        elif '\n' in org:
            del org[org.index('\n')]
        else:
            break
    for x in org:
        dscrp = x.replace('\n', '').strip()
        if dscrp.split(':')[0] == 'Organization Name':
            res[0] = dscrp.split(':')[1].strip()
        elif dscrp.split(':')[0] == 'Address':
            res[1] = dscrp.split(':')[1].strip()
            res[1] = res[1][:-22]
        elif dscrp.split(':')[0] == 'City, State Zip':
            res[2] = dscrp.split(':')[1].strip()
            res[2] = res[2].replace('\xa0', ' ')
            res[2] = res[2][:-15]
        elif dscrp.split(':')[0] == 'Phone':
            res[3] = dscrp.split(':')[1].strip()
            res[3] = res[3].replace('\xa0', ' ')[:-20]
    s = org[4:]
    s = ''.join(s).replace('\n', ' ')
    slc_ind = s.index('Services available:')
    s = s[:slc_ind]
    lst = ['Fax:', 'Toll-Free Phone:', 'Web Site:', 'Organization Description:', 'Service Description:', 'Population Description:']
    num_lst=[]
    findl = []
    for x in lst:
        if x in s:
            num_lst.append(s.index(x))
            findl.append(x)
    num_lst.append(len(s))
    for n in range(1, len(num_lst)):
        title = s[num_lst[n-1]:num_lst[n]]
        if findl[n-1] == "Fax:":
            res[4] = title[len(findl[n-1])+1:]
            res[4] = res[4].replace('\xa0', ' ')
        elif findl[n-1] == "Toll-Free Phone:":
            res[5] = title[len(findl[n-1])+1:]
            res[5] = res[5].replace('\xa0', ' ')
        elif findl[n-1] == "Web Site:":
            res[6] = title[len(findl[n-1])+1:]
        elif findl[n-1] == "Organization Description:":
            res[7] = title[len(findl[n-1])+1:]
        elif findl[n-1] == "Service Description:":
            res[8] = title[len(findl[n-1])+1:]
        elif findl[n-1] == "Population Description:":
            res[9] = title[len(findl[n-1])+1:]
    if 'No services are listed for this organization' not in org[-1].replace('\n', ' ').strip():
        res[-1] = org[-1].replace('\n', ' ').strip()
    big_one.append(res)


def save(args):
    print('%d results found' % len(args))
    workbook = xlsxwriter.Workbook('netofcare.xlsx', {'strings_to_urls': False})
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(30)
    worksheet.set_column('A:A', 40)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 30)
    worksheet.set_column('H:H', 40)
    worksheet.set_column('I:I', 40)
    worksheet.set_column('J:J', 40)
    worksheet.set_column('K:K', 40)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Organization Name', bold)
    worksheet.write('B1', 'Address', bold)
    worksheet.write('C1', 'City, State Zip', bold)
    worksheet.write('D1', 'Phone', bold)
    worksheet.write('E1', 'Fax', bold)
    worksheet.write('F1', 'Toll-Free Phone', bold)
    worksheet.write('G1', 'Web Site', bold)
    worksheet.write('H1', 'Organization Description', bold)
    worksheet.write('I1', 'Service Description', bold)
    worksheet.write('J1', 'Population Description', bold)
    worksheet.write('K1', 'Services available', bold)
    row = 1
    col = 0
    for x in range(len(args)):
        for y in range(11):
            worksheet.write(row, col+y, ''.join(args[x][y]))
        row += 1
    workbook.close()

for i in range(1, 135):
    url = 'http://www.netofcare.org/crd/default.asp?redo=yes&page=%d&sZip=10001&sTopic=&sMiles=50' % i
    get_data(url)

save(big_one)
