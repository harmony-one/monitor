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
            with open(raw_data, 'r') as f:
                out = ''.join([x.strip() for x in f])

            data = json.loads(out)
            if address in data.keys():
                return json.dumps(data[address])
            else:
                return f'\{"error":"address {address} not found"\}'
        else:
            return '{"error":"missing data file"}'

    stats = request.args.get('stats', '')
    if stats == 'true':
        if path.exists(net_stat):
            with open(net_stat, 'r') as f:
                out = ''.join([x.strip() for x in f])
            return out
        else:
            return '{"error":"missing data file"}'

    if path.exists(html_dis):
        with open(html_dis, 'r') as f:
            out = ''.join([x.strip() for x in f])
        return out
    return '{"error":"missing data file"}'
