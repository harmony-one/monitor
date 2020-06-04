import argparse
import csv

from os import (
    path
)

from jinja2 import (
    Environment,
    FileSystemLoader
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required = True, help = 'CSV file to read data from')
    parser.add_argument('--output', default = 'index.html', help = 'Name of output html file')
    parser.add_argument('--verbose', action = 'store_true', help = 'Verbose for debug')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    data = {}
    with open(args.input, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data[row[0]] = row[1]

    env = Environment(loader = FileSystemLoader('app/templates'))
    template = env.get_template('earning.html.j2')
    with open(args.output, 'w') as f:
        f.write(template.render(data = data))
