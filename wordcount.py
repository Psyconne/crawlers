# -*- coding: utf-8 -*-
import csv
import re


def count_word(line, word):
    """This function return the number of occurrences of the word within one line.
    The search of word is case-insensitive."""
    line = line.split(',', 102)[-1]
    pattern = re.compile(r',(\d+),(\d+),"')
    m = re.search(pattern, line)
    try:
        ind = line.index(m.group(0))
        line = line[:ind]
        line = re.sub(r'[^\w\s]', '', line)
        number = line.lower().count(' ' + word.lower() + ' ')
        return number
    except AttributeError:
        return 0


def words_one_line(line):
    try:
        line = line.split(',', 102)[-1]
        pattern = re.compile(r',(\d+),(\d+),"')
        m = re.search(pattern, line)
        ind = line.index(m.group(0))
        line = line[:ind]
        count = len(line.split(' '))
        return count
    except AttributeError:
        count = len(line.split(' '))
        return count


def write_new_csv(words):
    output = open('output.csv', 'w', encoding='utf-8')
    source_csv = open('input.csv', encoding='utf-8')
    words_str = ''
    for w in words:
        w = ',{}_count,{}_perc'.format(w, w)
        w = w.replace(' ', '_')
        words_str += w
    output.write(source_csv.readline()[:-1] + words_str + '\n')
    for row in source_csv:
        row = row[:-1]
        for x in range(len(words)):
            cnt = count_word(row, words[x])
            wol = words_one_line(row)
            row += ',' + str(cnt)
            row += ',' + str(check(cnt, wol))
        output.write(row + '\n')
    source_csv.close()
    output.close()


def check(a, b):
    if a == 0:
        return 0
    result = '%.2f' % (a / b * 100)
    return result


def main(words):
    if words is '':
        new_file = open('output.csv', 'w')
        writer = csv.writer(new_file, lineterminator='\n')
        headings = 'Please, enter the words...'
        writer.writerow([headings])
    else:
        write_new_csv(words.splitlines())
