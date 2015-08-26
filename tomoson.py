import urllib.request
import xlsxwriter
 
from bs4 import BeautifulSoup
 
 
URL = 'https://www.tomoson.com'
 
 
def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()
 
 
def get_page_count(html):
    soup = BeautifulSoup(html)
    pagination = soup.find('div', class_="pagination")
    links = pagination.find_all('a')
    count = int(links[-1].get('href')[-3:])
    return count


def parse(html):
    soup = BeautifulSoup(html)
    names = soup.find_all('a', target='_blank')
    names_list = {}
    for name in names:
        if "www.tomoson.com/business" in name.get('href'):
            names_list[name.text] = name.get('href')
    return names_list

 
def save(names, path):
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:A', 40)
    worksheet.set_column('B:B', 80)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Name', bold)
    worksheet.write('B1', 'Link', bold)
    row = 1
    col = 0
    for key, value in sorted(names.items()):
        worksheet.write(row, col, key)
        worksheet.write(row, col+1, names[key])
        row += 1
    workbook.close()

 
def main():
    total_pages = get_page_count(get_html(URL))
    print(total_pages)
    all_names = {}
    for n in range(1, total_pages + 1):
        page_url = URL + '/?user-type=bloggers&s=&page=' + str(n)
        names_from_page = parse(get_html(page_url))
        print('Parsing %d%% (%d/%d)' % (n / total_pages * 100, n, total_pages))
        all_names.update(names_from_page)
    print('Save...')
    save(all_names, 'profiles.xlsx')
 
 
if __name__ == '__main__':
    main()
