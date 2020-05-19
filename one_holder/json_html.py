#!/usr/bin/env python
# coding: utf-8


from os import path
from jinja2 import (
    Environment,
    FileSystemLoader
)

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'data'))
env = Environment(loader = FileSystemLoader(path.join(base, 'app', 'templates')), auto_reload = False)
template = env.get_template('one_holder_new.html.j2')
json_file = "/home/ubuntu/jupyter/monitor/one_holder/json/data.json"
with open(path.join(data, 'one_holder_new.html'), 'w', encoding = 'utf-8') as f:
    f.write(template.render(json = json_file))
print(f'-- Output HTML --')