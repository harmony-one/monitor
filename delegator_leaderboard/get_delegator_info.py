#!/usr/bin/env python
# coding: utf-8

import json
import os
import requests
import csv
import re
import datetime
import pandas as pd

from os import path
from collections import defaultdict
from threading import Thread

from jinja2 import (
    Environment,
    FileSystemLoader
)

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        content = json.loads(r.content)
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    if "error" in content:
        print("Error: The method does not exist/is not available")
        return None
    else:
        return content['result']

def getAllValidatorInformation():
    url = 'https://api.s0.os.hmny.io/'
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(url, method, params)

def getBalance(shard, address):
    url = endpoint[shard]
    method = "hmy_getBalance"
    params = [address, "latest"]
    res = get_information(url, method, params)
    if res != None:
        return int(res,16)/1e18

def getTransactionCount(shard, address):
    url = endpoint[shard]
    method = "hmy_getTransactionCount"
    params = [address, 'latest']
    res = get_information(url, method, params)
    if res != None:
        return int(res,16)

def getTransactionsCount(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmy_getTransactionsCount'
    params = [address, 'ALL']
    res = get_information(url, method, params)
    if res != None:
        return res

def getStakingTransactionCount(address):
    url = 'https://api.s0.os.hmny.io/'
    method = 'hmy_getStakingTransactionsCount'
    params = [address, 'ALL']
    return get_information(url, method, params)

def getEpoch():
    url = 'https://api.s0.os.hmny.io/'
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(url, method, params)
    return int(epoch, 16)

def read_csv(csv_file) -> (list):
    encoding = 'utf-8'
    r = requests.get(csv_file)
    s = [x.decode(encoding) for x in r.content.splitlines()]
    v = []
    for line in csv.reader(s):
        address = line[3].strip()
        if re.match('one1', address) != None:
            v.append(address)
    return v


if __name__ == "__main__":

#     endpoint = ['https://api.s0.os.hmny.io/', 'https://api.s1.os.hmny.io/', 'https://api.s2.os.hmny.io/', 'https://api.s3.os.hmny.io/']
    endpoint = ['http://54.215.128.188:9500', 'http://3.133.150.51:9500', 'http://3.91.3.73:9500','http://54.149.112.16:9500']

    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'data'))
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make data directory")
            exit(1)
    csvd = path.abspath(path.join(base, 'csv'))
    if not path.exists(csvd):
        try:
            os.mkdir(csvd)
        except:
            print("Could not make csv directory")
            exit(1)

    print("-- Data Processing --")
    validator_infos = getAllValidatorInformation()
    del_reward = defaultdict(int)
    del_stake = defaultdict(int)
    val_address = []
    epoch = getEpoch()
    # get the accumualted reward in current block
    for info in validator_infos:
        address = info['validator']['address']
        val_address.append(address)
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            del_reward[del_address] += reward
            amount = d['amount']/1e18
            del_stake[del_address] += amount

    del_address = set(del_reward.keys()) - set(val_address)
    balance = defaultdict(int)
    staking_transaction = defaultdict(int)
    normal_transaction = defaultdict(int)
    address_lst = list(del_address)
    thread_lst = defaultdict(list)
    for i in range(len(address_lst)):
        thread_lst[i%100].append(i)
    def collect_data(shard, x):
        global staking_transaction, normal_transaction, balance
        for i in thread_lst[x]:
            addr = address_lst[i]
            if shard == 0:
                staking_transaction[addr] = getStakingTransactionCount(addr)
            res = getBalance(shard, addr)
            if res != None:
                balance[addr] += res
                count = getTransactionCount(shard, addr)
                if count != None:
                    normal_transaction[addr] += count
    threads = []
    for x in range(100):
        for shard in range(len(endpoint)):
            threads.append(Thread(target = collect_data, args = [shard, x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance'])
    staking_transaction_df = pd.DataFrame(staking_transaction.items(), columns = ['address', 'staking-transaction-count'])
    normal_transaction_df = pd.DataFrame(normal_transaction.items(), columns = ['address', 'normal-transaction-count'])

    new_del_reward = dict()
    new_del_stake = dict()
    for k,v in del_reward.items():
        if k in del_address:
            new_del_reward[k] = v
            new_del_stake[k] = del_stake[k]
    reward_df = pd.DataFrame(new_del_reward.items(), columns=['address', 'lifetime-reward (total rewards - claim rewards)'])
    stake_df = pd.DataFrame(new_del_stake.items(), columns=['address', 'stake (total delegated stake)'])
    df = reward_df.join(stake_df.set_index('address'), on = 'address')
    df = df.join(balance_df.set_index('address'), on = 'address')
    df = df.join(staking_transaction_df.set_index('address'), on = 'address')
    df = df.join(normal_transaction_df.set_index('address'), on = 'address')
    time = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S")

    print("-- Filter the delegators in the google sheet --")
    html = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDAqXO-xVP4UwJlNJ6Qaws4N-TZ3FNZXqiSidPzU1I8pX5DS063d8h0jw84QhPmMDVBgKhopHhilFy/pub?gid=0&single=true&output=csv'
    delegator = read_csv(html)
    df['filter'] = df.apply(lambda c: True if c['address'] in delegator else False, axis = 1)
    print("-- Save csv files to ./csv/{:s}_delegator.csv --".format(time))
    df.to_csv(path.join(csvd, '{:s}_delegator.csv'.format(time)))

    filter_df = df[df['filter']].reset_index(drop = True)
    filter_df.to_csv(path.join(csvd, '{:s}_filter_delegator.csv'.format(time)))
    print("-- Save csv files to ./csv/{:s}_filter_delegator.csv --".format(time))

    env = Environment(loader = FileSystemLoader(path.join(base, 'app', 'templates')), auto_reload = False)
    template = env.get_template('delegator.html.j2')
    with open(path.join(data, 'delegator_rewards.html'), 'w', encoding = 'utf-8') as f:
        f.write(template.render(delegators = df))
    print(f'-- Output HTML --')
