#!/usr/bin/env python3

import argparse
import json, os
import requests
import time
import logging
import queue
from datetime import datetime
from collections import defaultdict
from os import path
from threading import Thread

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'data'))
json_log = path.join(data, 'commit.json')
backup_log = path.join(data, 'commit.json.bk')
file_time_fmt = '%m%d_%H%I%S'
read_time_fmt = '%m/%d_%H:%I:%S'
headers = {'Content-Type': 'application/json'}
config_file = path.abspath(path.join(base, 'network_information.txt'))

def latestBlock() -> dict:
    return {"id": "1", "jsonrpc": "2.0",
            "method": "hmy_latestHeader",
            "params": ["latest"]}

def nodeMetadata() -> dict:
    return {"id": "1", "jsonrpc": "2.0",
            "method": "hmy_getNodeMetadata",
            "params": []}

def request(endpoint, request, output = False) -> str:
    # Send request
    try:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(request), timeout = 5)
    except:
        return None
    if r.status_code != 200:
        return None
    return json.loads(r.content)['result']

if __name__ == '__main__':
    formatted_time = datetime.now().strftime(file_time_fmt)

    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', action = 'store_true', help = 'Generate sample config file')
    parser.add_argument('--sleep', default = 60, type = int, help = 'Sleep timer')
    parser.add_argument('--verbose', action = 'store_true', help = 'Verbose for debug')

    args = parser.parse_args()

    if args.setup:
        if not path.exists(config_file):
            with open(config_file, 'w') as f:
                f.write('mainnet, https://api.s0.t.hmny.io\n')
                f.write('mainnet, https://api.s1.t.hmny.io\n')
                f.write('mainnet, https://api.s2.t.hmny.io\n')
                f.write('mainnet, https://api.s3.t.hmny.io')
            print('Sample config file: %s' % config_file)
        else:
            print('Config file already exists: %s' % config_file)
        exit()

    if not path.exists(config_file):
        print('[ERROR] Missing config file: %s' % config_file)
        print('Use --setup to generate a sample file.')
        exit()

    networks = defaultdict(list)
    with open(config_file, 'r') as f:
        for l in f:
            try:
                net, endpoint = tuple(x.strip() for x in l.strip().split(','))
            except:
                print('[ERROR] Config file format does not match required format [network, endpoint]: %s' % l)
            networks[net].append(endpoint)

    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make directory data")
            exit(1)

    # Set up logger
    logger = logging.getLogger("commit_logger")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("data/%s" % ('commit_%s.log' % formatted_time))
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    commit_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # If log already exists, read existing data
    if path.exists(json_log):
        with open(json_log, 'r') as f:
            json_string = ''.join([x.strip() for x in f])
        existing_data = json.loads(json_string)
        for key in existing_data.keys():
            for shard in existing_data[key].keys():
                commit_data[key][shard] = existing_data[key][shard]

    def collect_data(network, endpoint, q):
        metadata = request(endpoint, nodeMetadata())
        block = request(endpoint, latestBlock())

        if metadata != None and block != None:
            commit = metadata['version']
            height = int(block['blockNumber'])
            shard = str(block['shardID'])
            timestamp = str(block['timestamp'])
            logger.info('Network: %s\tCommit: %s\tShard: %s\tBlock: %d\tTimestamp: %s' % (network, commit, shard, height, timestamp))
            q.put((network, commit, shard, height, timestamp))

    backup_counter = 0
    while True:
        try:
            if backup_counter > 10:
                logger.info("Creating backup log")
                with open(backup_log, 'w') as f:
                    json.dump(commit_data, f, sort_keys = True, indent = 4)
                backup_counter = 0
            else:
                backup_counter += 1
            threads = []
            q = queue.Queue(maxsize = 0)
            for n in networks.keys():
                for e in networks[n]:
                    threads.append(Thread(target = collect_data, args = (n, e, q)))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            while not q.empty():
                n, v, s, h, t = q.get()
                if not commit_data[n][v]:
                    commit_data[n][v]['first'] = t
                    commit_data[n][v]['first-block'] = h
                if h > commit_data[n][v][str(s)]:
                    commit_data[n][v]['latest'] = t
                    commit_data[n][v][str(s)] = h
            with open(json_log, 'w') as f:
                json.dump(commit_data, f, sort_keys = True, indent = 4)
            time.sleep(args.sleep)
        except Exception as e:
            logger.error("ERROR: %s" % e)
            pass
