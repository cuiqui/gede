"""
Retrieve declination for given word using wiktionary API.

"""
import re

import click
import requests
import tabulate
import bs4


API = 'http://de.wiktionary.org/w/api.php'


@click.command()
@click.argument('word')
@click.option('--table-fmt', type=click.Choice(tabulate.tabulate_formats),
              help='Visual text formatting for the output table',
              default='simple')
@click.option('-d', '--definition', is_flag=True,
              help='Retrieve definition')
def cli(word, definition, table_fmt):
    """Retrieve declination for given word in german."""

    response = requests.get(API, params={
        'action': 'parse',
        'format': 'json',
        'page': word
    })
    response.raise_for_status()

    if 'error' not in response.json():

        soup = bs4.BeautifulSoup(
            response.json()['parse']['text']['*'],
            'html.parser'
        )

        table = HtmlTableParser(
            soup, class_=re.compile(r'.*hintergrundfarbe2$'))
        table = table.parse()

        table.filter_empty()
        table.apply_filter('rows', r'.*Alle weiteren Formen.*')

        click.echo(tabulate.tabulate(
            table.rows, headers='firstrow', tablefmt=table_fmt) + '\n')

        if definition:
            bedeutungen = [e.get_text() for e in soup
                           .find('p', title='Sinn und Bezeichnetes (Semantik)')
                           .find_next_sibling('dl')
                           .find_all('dd')]

            click.secho('Definition', fg='bright_cyan')
            click.echo('\n'.join(bedeutungen))
    else:
        click.secho('Error for word "{}". Code: {}. Info: {}'.format(
            word.encode('utf-8'),
            response.json()['error'].get('code', 'unknown'),
            response.json()['error'].get('info', 'unknown')), fg='yellow')


class HtmlTableParser(object):
    """Given an html and keyword arguments accepted
    in find method of BeautifulSoup, get table and
    return a Table object.

    """

    def __init__(self, html, **kwargs):
        self.html = html
        self.kwargs = kwargs
        self.table = None

    def parse(self):
        """Parse an html table. Return a Table object"""

        self.table = self.html.find(**self.kwargs)

        if self.table is None:
            raise click.ClickException(
                'No table was found for query: {}'.format(str(self.kwargs)))

        rows = []
        rowspan = {}
        for row in self.table.find_all('tr'):
            current = []
            c_cell = 0
            for cell in row.find_all(re.compile(r'(th|td)')):

                if c_cell in rowspan and rowspan[c_cell] > 0:
                    current.append('')
                    rowspan[c_cell] -= 1

                if cell.name == 'th':
                    current.append(click.style(
                        cell.get_text().replace('\n', ' '), fg='bright_blue'))
                else:
                    current.append(cell.get_text().replace('\n', ' '))

                if cell.has_attr('colspan'):
                    current.extend('' for i in range(
                        int(cell['colspan']) - 1))

                if cell.has_attr('rowspan'):
                    rowspan[c_cell] = int(cell['rowspan']) - 1

                c_cell += 1
            rows.append(current)

        return Table(rows)

    @property
    def html(self):
        """Proper HTML """
        return self._html

    @html.setter
    def html(self, val):
        """Verify that html is actually a bs4 object """
        if not isinstance(val, bs4.element.Tag):
            raise ValueError(
                '"{}" is not an instance of bs4.element.Tag'.format(val))

        self._html = val


class Table(object):
    """Table object for easy dealing with rows, columns
    and filters

    """

    def __init__(self, data):
        self.rows = data
        self.columns = list(zip(*data))

    def filter_empty(self):
        """ Filter empty values from columns and rows """

        for col in self.columns[:]:
            if all(val == '' for val in col):
                for row in self.rows:
                    del row[self.columns.index(col)]
                del self.columns[self.columns.index(col)]

    def apply_filter(self, data_item, regex):
        """ Apply filter to row or column """

        try:
            regex = re.compile(regex)
        except ValueError:
            raise click.ClickException(
                'Could not compile regular expression "{}"'.format(regex))

        if data_item == 'rows':
            self.rows = [e for e in self.rows
                         if not any(regex.match(i) for i in e)]
            self.columns = list(zip(*self.rows))

        if data_item == 'columns':
            for col in self.columns[:]:
                if any(regex.match(val) for val in col):
                    for row in self.rows:
                        del row[self.columns.index(col)]
                    del self.columns[self.columns.index(col)]
