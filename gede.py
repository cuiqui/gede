"""
Retrieve declination for given word.

"""
import re

import click
import requests
import bs4
import tabulate


API = 'http://de.wiktionary.org/w/api.php'


@click.command()
@click.argument('word', type=unicode)
@click.option('--table-fmt', type=click.Choice(tabulate.tabulate_formats),
              help='Visual text formatting for the output table',
              default='simple')
def cli(word, table_fmt):
    """Retrieve declination for given word in german.

    Specifications:

        Substantive: singular, first letter should be capital.

        Adjective: singular, masculine.

        Verb: infinitive.

        Pronoun: masculine, singular.

    """
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
        table = soup.find(class_=re.compile(r'.*hintergrundfarbe2$'))

        if table is not None:
            rows = []
            rowspan = {}
            for row in table.find_all('tr'):
                current = []
                c_cell = 0
                for cell in row.find_all(re.compile(r'(th|td)')):

                    if str(c_cell) in rowspan and rowspan[str(c_cell)] > 0:
                        current.append('')
                        rowspan[str(c_cell)] -= 1

                    if cell.name == 'th':
                        current.append(click.style(
                            cell.get_text().replace('\n', ' '), fg='blue'))
                    else:
                        current.append(cell.get_text().replace('\n', ' '))

                    if cell.has_attr('colspan'):
                        current.extend('' for i in range(
                            int(cell['colspan']) - 1))

                    if cell.has_attr('rowspan'):
                        rowspan[str(c_cell)] = int(cell['rowspan']) - 1

                    c_cell += 1
                rows.append(current)

            filter_out = [r'.*Alle weiteren Formen.*']

            data = (e for e in rows
                    if not any(re.compile(f).match(i)
                               for f in filter_out for i in e))

            click.echo(tabulate.tabulate(
                [e for e in data], headers='firstrow', tablefmt=table_fmt))
        else:
            click.secho('No results for word "{}". '.format(word) +
                        'Are you sure it meets the specifications?',
                        fg='yellow')
    else:
        click.secho('Error for word "{}". Code: {}. Info: {}'.format(
            word.encode('utf-8'),
            response.json()['error'].get('code', 'unknown'),
            response.json()['error'].get('info', 'unknown')), fg='yellow')
