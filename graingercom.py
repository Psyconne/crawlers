from bs4 import BeautifulSoup
import requests
import csv

csvfile =  open('grainger.csv', 'w', encoding='utf-8')
writer = csv.writer(csvfile, lineterminator='\n')
writer.writerow(('Item description', 'Brand', 'Item no', 'Part no', 'Price',
                 'Photo (url)', 'Availability'))
th_url = 'http://www.grainger.com/category/hvac-and-refrigeration/ecatalog/N-k00?bc=y'
sec_url = 'http://www.grainger.com/category/a-c-refrigeration/hvac-and-refrigeration/ecatalog/N-jn4?bc=y'
url = 'http://www.grainger.com/category/halogen-leak-detectors/a-c-refrigeration/hvac-and-refrigeration/ecatalog/N-jnf?perPage=48&requestedPage=1'

def parse(url):
    print(url)
    price = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    for x in soup.find_all('span', class_='gcprice-value'):
        price.append(x.text)
    z = 0
    for x in soup.find_all('ul',  class_="productDescription"):
        try:
            desc = x.find('p', class_="LD hidden").text
        except AttributeError:
            desc = x.find('div', class_="longDesc").text
        brand = x.find('li', class_="productBrand").text
        # print('Item #' + x.find('span', class_="productInfoValueList").text)
        item = x.find('li', class_="product-info").text
        part = x.find('span', class_="productMFR").text
        link = x.find('a').get('href')
        i = link.find('//') + 2
        link = link[i:-9]
        writer.writerow([desc, brand, item, part, price[z], link, 'true'])
        z += 1

def find_urls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, from_encoding='utf-8')
    reslt = []
    for x in soup.find('ul', class_="filter-list-item").find_all('a'):
        if 'javascript' not in x.get('href'):
            reslt.append('http://www.grainger.com' + x.get('href'))
            print('http://www.grainger.com' + x.get('href'))
    return reslt


if __name__ == '__main__':
    anth = find_urls(th_url)
    for a in anth:
        try:
            r = find_urls(a)
            for x in r:
                parse(x)
                # print(x)
        except AttributeError:
            continue
    csvfile.close()
