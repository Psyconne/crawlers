from bs4 import BeautifulSoup
import urllib.request
import re
import csv

main_url = 'http://www.visitphilly.com/things-to-do/'
names_of_category = ['Museums & Attractions', 'Restaurants & Dining',
                     'History', 'Nightlife', 'Shopping', 'Hotels', 'Music & Art']
visit = 'http://www.visitphilly.com'


with open('visitphilly.csv', 'w', encoding='utf8') as csvfile:
    writer = csv.writer(csvfile, lineterminator='\n')
    writer.writerow(('Category', 'Subcategory', 'Name', 'Address', 'Phone number', 'Website', 'Image URL'))


def get_categories(url, names):
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code)
    categories = {}
    source_links = soup.find('ul', class_="nav")
    for link in source_links.find_all('a'):
        categories[link.text] = link.get('href')
    clear_categories = {}
    for name in names:
        clear_categories[name] = [categories[name]]
    return clear_categories


def get_subcategory(url):
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code)
    source_links = soup.find('ul', class_="nav")
    names = []
    for link in source_links.find_all('a', class_='modstructure'):
        names.append(link.text)
    urls = []
    for link in source_links.find_all('a'):
        urls.append(link.get('href'))
    urls = urls[:-1]
    result = dict(zip(names, urls))
    return result


def view_items(url):
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code)
    name = soup.find_all('h1', class_='alpha')[1]
    name = name.text
    links = []
    result = []
    dictionary = {}
    pattern = ('/nightlife', '/music', '/museums', '/shopping', '/restaurants', '/history', '/hotels',)
    source_links = soup.findAll('a', title='Continue reading')
    for l in source_links:
        l = l.get('href')
        if visit in l:
            l = l[26:-1]
        if l not in links and l.startswith(pattern):
            links.append(l)
    for l in links:
        result.append(visit + l + '/')
    # dictionary[name] = result
    return result


def get_item(url):
    try:
        source_code = urllib.request.urlopen(url).read()
    except urllib.error.HTTPError:
        source_code = ''
    soup = BeautifulSoup(source_code)
    if not (len(soup)):
        return ['Page not found']
    else:
        name = soup.find('h1', class_='alpha')
        name = name.text
        address = soup.find('p', class_='details')
        try:
            website = address.find('a').get('href')
        except AttributeError:
            website = 'No website'
        try:
            pattern = re.compile(r'\D*(\d{0,4})\D*(\d{3})-(\d{4})')
            phone_number = pattern.search(address.text).groups()
            if phone_number:
                remove = address.text.split().index(('(' + phone_number[0] + ')'))
                address = ' '.join(address.text.split()[:remove]).strip().replace(',', '')
                phone_number = '(' + phone_number[0] + ') ' + phone_number[1] + '-' + phone_number[2]
            else:
                phone_number = 'No phone number'
        except ValueError:
            for l in address.text.split():
                if phone_number[0] in l:
                    remove = address.text.split().index(l)
                    address = ' '.join(address.text.split()[:remove]).strip().replace(',', '')
                    phone_number = phone_number[0] + '-' + phone_number[1] + '-' + phone_number[2]
        except IndexError:
            phone_number = 'No phone number'
        except AttributeError:
            address = ' '.join(address.text.split()[:-1]).strip().replace(',', '')
            phone_number = 'No phone number'
        image_url = soup.find('img', class_='slideshow-main')
        try:
            image_url = visit + image_url.get('src')
        except AttributeError:
            image_url = 'No image'
        result = [name, address, phone_number, website, image_url]
        return result


def write_to_file(dictionary):
    with open('visitphilly.csv', 'a', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        for key in sorted(dictionary):
            if not (dictionary[key] == ['Page not found']):
                writer.writerow((key[0], key[1], ', '.join(dictionary[key])))


def main():
    dict_categories = get_categories(main_url, names_of_category)
    for x, y in sorted(dict_categories.items()):
        dict_categories[x] = (get_subcategory(y[0]))
    del dict_categories['Restaurants & Dining']['Authentic Philadelphia Hoagies']
    del dict_categories['Hotels']['Other Accommodations']
    dict_items = {}
    for cat in list(sorted(dict_categories.keys())):
        for sub in list(sorted(dict_categories[cat].keys())):
            dict_items[(cat, sub)] = view_items(dict_categories[cat][sub])
    # with open ('visitphilly_links.csv', 'w') as f:
    #     wr = csv.writer(f, lineterminator='\n')
    #     for key, value in sorted(dict_items.items()):
    #         for v in value:
    #             wr.writerow((key, v))
    final_dict = {}
    for cat in dict_items:
        for link in dict_items[cat]:
            print(link)
            try:
                final_dict[cat] = get_item(link)
                write_to_file(final_dict)
            except urllib.error.HTTPError:
                pass
            except Exception:
                pass

main()



