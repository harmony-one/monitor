#!/usr/bin/env python3

# Usage: python3 validator_stats.py

import csv
import json
import argparse
import requests
import re
from collections import defaultdict
from queue import Queue
from threading import Thread

csv_link = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUUOCAuSgP8TcA1xWY5AbxaMO7OSowYgdvaHpeMQudAZkHkJrf2sGE6TZ0hIbcy20qpZHmlC8HhCw1/pub?gid=0&single=true&output=csv'
encoding = 'utf-8'
groups = ['team', 'p-ops', 'foundational nodes', 'p-volunteer', 'hackers', 'community', 'partners']
headers = {'Content-Type': 'application/json'}

def get_all_validators(endpoint) -> list:
    v_print("-- hmy_getAllValidatorAddresses --")
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getAllValidatorAddresses",
               "params": []}
    r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 30)
    return json.loads(r.content)['result']

def get_all_keys(endpoint) -> dict:
    v_print("-- hmy_getSuperCommittees --")
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getSuperCommittees",
               "params": []}
    r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 30)
    return json.loads(r.content)['result']

def read_csv(csv_file) -> (dict, list):
    v_print("-- Processing CSV --")
    r = requests.get(csv_file)
    s = [x.decode(encoding) for x in r.content.splitlines()]
    d = defaultdict(list)
    v = []
    dup_list = []
    for line in csv.reader(s):
        group = line[0].strip()
        email = line[2].strip()
        address = line[6].strip()
        if group in groups and re.match('one1', address) != None:
            if re.search('/[0-9]+$',  email) != None or re.search('www.ankr.com', email) != None:
                v_print("Skipping: %s" % address)
                dup_list.append(address)
            else:
                v_print("Adding: %s" % address)
                d[group].append(address)
                v.append(address)
    return d, v, dup_list

def get_validator_information(endpoint, validators) -> dict:
    v_print("-- hmy_getValidatorInformation --")
    validator_information = {}
    def collect_validator_information(validator, endpoint, q):
        payload = {"id": "1", "jsonrpc": "2.0",
                   "method": "hmy_getValidatorInformation",
                   "params": [validator]}
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 30)
        try:
            q.put((validator, json.loads(r.content)['result']))
        except:
            q.put((validator, None))
    threads = []
    q = Queue(maxsize = 0)
    for v in validators:
        v_print("Address: %s" % v)
        threads.append(Thread(target = collect_validator_information, args = (v, endpoint, q)))
    batch = []
    for t in threads:
        batch.append(t)
        t.start()
        if len(batch) == 10:
            for b in batch:
                b.join()
            batch = []
    for b in batch:
        b.join()
    while not q.empty():
        val, out = q.get()
        validator_information[val] = out
    return validator_information

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', default = 'https://api.s0.os.hmny.io', help = 'Network endpoint')
    parser.add_argument('--csv_link', default = csv_link, help = 'File to read for groups & addresses')
    parser.add_argument('--verbose', default = False, action = 'store_true', help = 'Verbose print for debug')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    network_validators = get_all_validators(args.endpoint)
    committee = get_all_keys(args.endpoint)
    by_group, csv_validators, extra_validators = read_csv(args.csv_link)
    new_validators = [x for x in network_validators if x not in csv_validators and x not in extra_validators]
    validator_information = get_validator_information(args.endpoint, network_validators)

    v_print("-- Processing data --")
    external_bls_keys = []
    for x in committee['current']['quorum-deciders'].keys():
        for y in committee['current']['quorum-deciders'][x]['committee-members']:
            if not y['is-harmony-slot']:
                external_bls_keys.append(y['bls-public-key'])

    current_validators = [v for v in network_validators if validator_information[v]['currently-in-committee'] > 0]
    earned_validators = [v for v in network_validators if validator_information[v]['lifetime']['reward-accumulated'] > 0]

    per_group_earning_validators = defaultdict(list)
    per_group_created_validators = defaultdict(list)
    per_group_elected_validators = defaultdict(list)

    for g in by_group.keys():
        for v in by_group[g]:
            if v in validator_information.keys():
                per_group_created_validators[g].append(v)
                if validator_information[v]['lifetime']['reward-accumulated'] > 0:
                    per_group_earning_validators[g].append(v)
                if validator_information[v]['currently-in-committee']:
                    per_group_elected_validators[g].append(v)

    print("-- Total Validator Stats --")
    print("Total created validators: %d" % len(network_validators))
    print("Validators that have earned rewards: %d" % len(earned_validators))
    print("Current validators: %d" % len(current_validators))
    print("Current keys in committee: %d" % len(external_bls_keys))

    print()

    print("-- Created Validators Per Group --")
    total_csv_created_validators = 0
    for g in per_group_created_validators.keys():
        c = len(per_group_created_validators[g])
        print("Group: %-20s Number: %d" % (g, c))
        total_csv_created_validators += c
    print("Total: %d" % total_csv_created_validators)

    print()

    print("-- Earned Validators Per Group --")
    total_csv_earned_validators = 0
    for g in per_group_earning_validators.keys():
        c = len(per_group_earning_validators[g])
        print("Group: %-20s Number: %d" % (g, c))
        total_csv_earned_validators += c
    print("Total: %d" % total_csv_earned_validators)

    print()

    print("-- Elected Validators Per Group")
    total_csv_elected_validators = 0
    for g in per_group_elected_validators.keys():
        c = len(per_group_elected_validators[g])
        print("Group: %-20s Number: %d" % (g, c))
        total_csv_elected_validators += c
    print("Total: %d" % total_csv_elected_validators)

    print()

    print("-- New Validators --")
    print("New Validators: %d" % len(new_validators))
    for n in new_validators:
        print("Address: %s, Validator Name: %s, Security Contact: %s, Website: %s" % (n, validator_information[n]['validator']['name'], validator_information[n]['validator']['security-contact'], validator_information[n]['validator']['website']))
