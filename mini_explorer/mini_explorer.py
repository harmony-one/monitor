#!/usr/bin/env python3

import argparse
import json
import requests
import time
import logging
import os
from os import path
from threading import Thread
from collections import defaultdict

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'data'))

def latestBlock() -> dict:
    return {"id": "1", "jsonrpc": "2.0",
            "method": "hmy_latestHeader",
            "params": ["latest"]}

def blockByHash(hash) -> dict:
    return {"id": "1", "jsonrpc": "2.0",
            "method": "hmy_getBlockByHash",
            "params": [hash, True]}

def request(endpoint, request, output = False) -> str:
    # Send request
    r = requests.get(endpoint, headers = {'Content-Type':'application/json; charset=utf8'}, data = request)
    # Check for invalid status code
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None

    # Check for valid JSON format return
    try:
        r.json()
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None

    return r.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', required = True, help = 'File name for data log')
    parser.add_argument('--endpoints', help = 'Endpoints to query from, sorted by shard & seperated by commas')
    parser.add_argument('--endpoint_file', help = 'List of endpoints, sorted by shard & seperated by new lines')
    parser.add_argument('--no_staking', action = 'store_true', help = 'Disable check for staking transactions')
    parser.add_argument('--sleep', default = 4, type = int, help = 'Sleep timer')

    args = parser.parse_args()

    if not args.endpoints and not args.endpoint_file:
        print('Either endpoint file or list of endpoints is required.')
        exit(1)

    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]
    else:
        try:
            with open(args.endpoint_file, 'r', encoding = 'utf-8') as f:
                endpoint = [x.strip() for x in f]
        except FileNotFoundError:
            print('Given file not found: %s' % args.endpoint_file)
            exit(1)

    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make data directory")
            exit(1)

    # Set up logger
    logger = logging.getLogger("mini_explorer")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(path.join(data, args.output_file))
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    try:
        while True:
            def collect_data(shard):
                result = request(endpoint[shard], json.dumps(latestBlock()))
                if result != None:
                    hash = result["result"]["blockHash"]
                    next = request(endpoint[shard], json.dumps(blockByHash(hash)))
                    if next != None:
                        sx = defaultdict(int)
                        if not args.no_staking:
                            sx["total"] = len(next["result"]["stakingTransactions"])
                            for t in next["result"]["stakingTransactions"]:
                                sx[t["type"]] += 1
                        t = {"shard": shard,
                             "leader": result["result"]["leader"],
                             "timestamp": result["result"]["timestamp"],
                             "block": result["result"]["blockNumber"],
                             "epoch": result["result"]["epoch"],
                             "gas": int(next["result"]["gasUsed"], 0),
                             "maxGas": int(next["result"]["gasLimit"], 0),
                             "size": int(next["result"]["size"], 0),
                             "transactions": len(next["result"]["transactions"]),
                             "staking": sx}
                        logger.info(json.dumps(t))
            threads = []
            for x in range(len(endpoint)):
                threads.append(Thread(target = collect_data, args = [x]))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        pass
