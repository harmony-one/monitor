import json
from os import path
from flask import request
from app import app

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, '..', 'data'))

html_dis = path.join(data, 'earning.html')
raw_data = path.join(data, 'validator_info.json')
net_stat = path.join(data, 'network_stats.json')

@app.route('/validators')
def validator_info():

    address = request.args.get('address', '')
    if address != '':
        if path.exists(raw_data):
            with open(raw_data, 'r', encoding = 'utf-8') as f:
                out = ''.join([x.strip() for x in f])
            data = json.loads(out)
            if address in data.keys():
                return json.dumps(data[address])
            else:
                return json.dumps({'error': f'address {address} not found'})
        else:
            return missing_data_error()

    stats = request.args.get('stats', '')
    if stats == 'true':
        if path.exists(net_stat):
            with open(net_stat, 'r', encoding = 'utf-8') as f:
                out = ''.join([x.strip() for x in f])
            return json.dumps(json.loads(out))
        else:
            return missing_data_error()

    if path.exists(html_dis):
        with open(html_dis, 'r' , encoding = 'utf-8') as f:
            html = '\n'.join(f.readlines())
        return html
    return missing_data_error()

def missing_data_error():
    return json.dumps({'error': 'missing data file'})
