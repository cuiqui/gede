"""
Retrieve plurals for given word
"""
import re
import io
from HTMLParser import HTMLParser

import click
import requests
import bs4
import tabulate


API = 'http://de.wiktionary.org/w/api.php'


@click.command()
@click.argument('word')
def cli(word):
    """Look for the definition of a word in RAE dictionary
    """
    response = requests.get(API, params={
        'action': 'parse',
        'format': 'json',
        'page': word
    })
    response.raise_for_status()

    if 'error' not in response.json():

        soup = bs4.BeautifulSoup(response.json()['parse']['text']['*'], 'html.parser')
        table = soup.find(class_=re.compile(r'.*hintergrundfarbe2$'))
        all_rows = table.find_all('tr')

        matrix = [[None for _ in range(max(len(row.find_all(re.compile(r'(th|td)')))
                  for row in all_rows))] for _ in range(len(all_rows))]

        crow = 0
        rowspans = []
        for row in table.find_all('tr'):

            ccell = 0
            for cell in row.find_all(re.compile(r'(th|td)')):
                if matrix[crow][ccell] == '':
                    ccell += 1
                if cell.has_attr('rowspan'):
                    matrix[crow][ccell] = cell.get_text()
                    for x in range(crow + 1, crow + int(cell['rowspan'])):
                        matrix[x][ccell] = ''

                if matrix[crow][ccell] is None:
                    matrix[crow][ccell] = cell.get_text()

                    #rowspans.extend([x, ccell] for x in range(crow, crow + int(cell['rowspan'])))
                #matrix[crow][ccell] = cell.get_text()

                #if cell.has_attr('rowspan'):
                #    ccell +=
                #print crow, ccell, cell.get_text()
                #matrix[crow][ccell] = cell.get_text()

                #if cell.has_attr('colspan'):
                #     colspans.extend([crow, y] for y in range(ccell, ccell + int(cell['colspan'])))
                     #build_row.extend([cell.get_text()] + ['' for e in range(int(cell['colspan']) - 1)])
                #if cell.has_attr('rowspan'):
                #     rowspans.extend([x, ccell] for x in range(crow, crow + int(cell['rowspan'])))
                # else:
                #     build_row.append(cell.get_text())
                ccell += 1
            #print empty_matrix
            crow += 1
            #rows.append(build_row)
        print matrix
        print tabulate.tabulate(matrix, headers='firstrow')
        get_max_dimensions(table)
        #        print cell.string
        #    print extract_string(cell, ',')
        #rows.append([''.join(cell.get_text()) for cell in row.find_all(re.compile(r'(th|td)'))])

        #print tabulate.tabulate(rows, headers='firstrow')
        #print rows
        #parser = Parser()
        #data = parser.parse()
        #click.echo(tabulate.tabulate(data, headers='firstrow'))
    else:
        click.secho('Error for word "{}". Code: {}. Info: {}'.format(
            word,
            response.json()['error'].get('code', 'unknown'),
            response.json()['error'].get('info', 'unknown')), fg='yellow')


def get_max_dimensions(table):
    if not isinstance(table, bs4.element.Tag):
        raise click.ClickException('{} is not an instance of "bs4.element.Tag"'.format(table))

    all_rows = table.find_all('tr')

    colspans = [int(cell['colspan']) for row in all_rows
                for cell in row.find_all(re.compile(r'(th|td)'))
                if cell.has_attr('colspan')]

    rowspan = [int(cell['rowspan']) for row in all_rows
               for cell in row.find_all(re.compile(r'(th|td)'))
               if cell.has_attr('rowspan')]

    print colspans, rowspan

def extract_string(cell, separator):
    data = []
    for content in cell.contents:
        if isinstance(content, bs4.element.NavigableString):
            data.append(io.StringIO(content.stripped_strings))
        elif isinstance(content, bs4.element.Tag):
            extract_string(content, separator)
        else:
            print content
    return separator.join([v.getvalue() for v in data])

class Parser(HTMLParser):
    """Parse german declination table in wiktionary"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.entries, self.current = [], []
        self.data = None
        self.record = False
        self.mapping = {
            'tr': self.add_row,
            'th': self.add_entry,
            'td': self.add_entry,
            'table': self.stop_recording
        }

    def parse(self, html):
        self.feed(html)
        return self.entries

    def handle_starttag(self, tag, attrs):
        if self.record:
            if tag in ('th', 'td'):
                self.data = io.StringIO()

        if tag == 'table' and self._is_decl_table(attrs):
            self.record = True

    def handle_data(self, data):
        if self.data is not None:
            self.data.write(data.replace('\n', ' '))

    def handle_endtag(self, tag):
        self.mapping.get(tag, lambda: None)()

    def add_row(self):
        if self.current:
            self.entries.append(self.current)
            self.current = []

    def add_entry(self):
        if self.data:
            self.current.append(self.data.getvalue())
            self.data = None

    def stop_recording(self):
        self.record = False

    def _is_decl_table(self, attrs):
        regexp = re.compile(r'.*hintergrundfarbe2$')
        class_name = dict(attrs).get('class', '')
        return regexp.match(class_name)
