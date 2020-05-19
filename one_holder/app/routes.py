import json
from os import path
from app import app

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, '..', 'data'))

html_dis = path.join(data, 'one_holder.html')

@app.route('/one_holder')
def delegator():
    if path.exists(html_dis):
        with open(html_dis, 'r' , encoding = 'utf-8') as f:
            html = '\n'.join(f.readlines())
        return html
    return missing_data_error()

def missing_data_error():
    return json.dumps({'error': 'missing data file'})
