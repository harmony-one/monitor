#!/usr/bin/env python3

import argparse
import csv
import gzip
import json
import logging
import logging.handlers
import os
import re
import requests

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from glob import glob
from os import path
from time import sleep
from multiprocessing.pool import ThreadPool


base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'data'))

block_log = path.join(data, 'block.log')
rpc_log = path.join(data, 'account_rpc.log')
validator_log = path.join(data, 'validator.log')

headers = {'Content-Type': 'application/json'}

# Autonode/util.py
class _GZipRotator:
    """A simple zip rotator for logging"""

    def __call__(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)

def get_simple_rotating_log_handler(log_file_path):
    """
    A simple log handler with no level support.
    Used purely for the output rotation.
    """
    log_formatter = logging.Formatter('%(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when = 'h', interval = 4, encoding = 'utf8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(log_formatter)
    handler.rotator = _GZipRotator()
    return handler

def get_node_metadata(endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getNodeMetadata",
               "params": []}
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
        try:
            out = json.loads(r.content)['result']
            return out
        except Exception as e:
            pass
        retries = retries - 1
    return None


def get_block_by_number(block_num, endpoint, retries, get_tx_info = False):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getBlockByNumber",
               "params": [str(hex(block_num)), get_tx_info]}
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
        try:
            out = json.loads(r.content)['result']
            return block_num, out
        except Exception as e:
            print(e)
            pass
        retries = retries - 1
    return block_num, None

def get_delegation_by_delegator(delegator_addr, endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getDelegationsByDelegator",
               "params": [delegator_addr]}
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
        try:
            out = json.loads(r.content)['result']
            return delegator_addr, out
        except Exception as e:
            print(f'{e}')
            pass
        retries = retries - 1
    return delegator_addr, None

# TODO: Swap to this after implemented
def get_delegation_by_delegator_by_block(delegator_addr, block_num, endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_GetDelegationsByDelegatorByBlockNumber",
               "params": [delegator_addr, str(hex(block_num))]}
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
        try:
            out = json.loads(r.content)['result']
            return delegator_addr, out
        except Exception:
            pass
        retries = retries - 1
    return delegator_addr, None

def get_balance_at_block(addr, block_num, endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getBalanceByBlockNumber",
               "params": [addr, str(hex(block_num))]}
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
        try:
            out = json.loads(r.content)['result']
            return addr, out
        except Exception:
            pass
        retries = retries - 1
    return addr, None

def get_latest_header(endpoint):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_latestHeader",
               "params": []}
    r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 10)
    try:
        out = json.loads(r.content)['result']
        return out
    except Exception:
        return None

def get_all_validators_addresses(endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getAllValidatorAddresses",
               "params": []}
    # Set timeout high in case of many validators
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 300)
        try:
            out = json.loads(r.content)['result']
            return out
        except Exception:
            pass
        retries = retries - 1
    return None

def get_validator_information_by_block(validator_addr, block_num, endpoint, retries):
    payload = {"id": "1", "jsonrpc": "2.0",
               "method": "hmy_getValidatorInformationByBlockNumber",
               "params": [validator_addr, str(hex(block_num))]}
    # Set timeout high in case of many validators
    while retries >= 0:
        r = requests.request('POST', endpoint, headers = headers, data = json.dumps(payload), timeout = 300)
        try:
            out = json.loads(r.content)['result']
            return validator_addr, out
        except Exception:
            pass
        retries = retries - 1
    return validator_addr, None

def convert_atto_to_one(atto):
    return Decimal(atto) / Decimal(1e18)

def get_blockchain(start_block, end_block, endpoint, retries):
    v_print(f'[get_blockchain] Start Block: {start_block}, End Block: {end_block}, Num Blocks: {end_block - start_block}')
    logger = logging.getLogger("blockchain")
    logger.setLevel(logging.DEBUG)
    active_accounts = set()

    pool = ThreadPool()
    threads = []
    for block_num in range(start_block, end_block):
        threads.append(pool.apply_async(get_block_by_number, (block_num, endpoint, retries, True)))

    for t in threads:
        num, block = t.get()
        if block is not None:
            try:
                transactions = block['transactions']
                staking_transactions = block['stakingTransactions']

                # Only track accounts that have sent at least one staking transaction
                # for tx in transactions:
                    # active_accounts.add(tx['from'])
                    # active_accounts.add(tx['to'])
                for stx in staking_transactions:
                    active_accounts.add(stx['from'])

                logger.debug(json.dumps(block, sort_keys = True, indent = 4))
            except Exception as e:
                err = {'error': f'error parsing output for block #{num}',
                       'reply': block}
                logger.debug(json.dumps(err, sort_keys = True, indent = 4))
        else:
            err = {'error': f'unable to fetch block #{num} after {retries} tries'}
            logger.debug(json.dumps(err, sort_keys = True, indent = 4))

    return active_accounts

def create_account_snapshot(account_list, block_num, epoch, endpoint, output_file, retries):
    v_print(f'[create_account_snapshot] Num accounts: {len(account_list)}, Block Number: {block_num}')
    logger = logging.getLogger('rpc')
    logger.setLevel(logging.DEBUG)

    delegator_pool = ThreadPool()
    delegator_threads = []
    account_data = defaultdict(dict)
    for addr in account_list:
        delegator_threads.append(delegator_pool.apply_async(get_delegation_by_delegator, (addr, endpoint, retries)))
        # threads.append(pool.apply_async(get_delegation_by_delegator_by_block, (addr, block_num, args.endpoint, retries)))

    for t in delegator_threads:
        addr, delegation = t.get()
        if delegation is not None:
            total_delegation = Decimal(0)
            total_undelegations = Decimal(0)
            total_rewards = Decimal(0)
            try:
                for d in delegation:
                    total_delegation = total_delegation + convert_atto_to_one(d['amount'])
                    total_rewards = total_rewards + convert_atto_to_one(d['reward'])
                    # TODO: Double check undelegations format
                    for u in d['Undelegations']:
                        if epoch - u['epoch'] <= 7:
                            total_undelegations = total_undelegations + convert_atto_to_one(u['amount'])
                account_data[addr]['total-delegations'] = total_delegation
                account_data[addr]['total-undelegations'] = total_undelegations
                account_data[addr]['total-rewards'] = total_rewards
                logger.debug(json.dumps(delegation, sort_keys = True, indent = 4))
            except Exception as e:
                account_data[addr]['total-delegations'] = 'NAN'
                account_data[addr]['total-undelegations'] = 'NAN'
                account_data[addr]['total-rewards'] = 'NAN'
                err = {'error': f'error parsing delegation output for {addr}',
                       'reply': delegation}
                logger.debug(json.dumps(err, sort_keys = True, indent = 4))
        else:
            account_data[addr]['total-delegations'] = 'NAN'
            account_data[addr]['total-undelegations'] = 'NAN'
            account_data[addr]['total-rewards'] = 'NAN'
            err = {'error': f'unable to fetch delegations for {addr} after {retries} tries'}
            logger.debug(json.dumps(err, sort_keys = True, indent = 4))

    balance_pool = ThreadPool()
    balance_threads = []
    for addr in account_list:
        balance_threads.append(balance_pool.apply_async(get_balance_at_block, (addr, block_num, endpoint, retries)))

    for t in balance_threads:
        addr, balance = t.get()
        if balance is not None:
            try:
                account_data[addr]['balance'] = convert_atto_to_one(int(balance, 0))
                account_data[addr]['total-balance'] = sum([x for x in account_data[addr].values() if isinstance(x, Decimal)])
                formatted_balance = {'address': addr, 'balance': balance}
                logger.debug(json.dumps(formatted_balance, sort_keys = True, indent = 4))
            except Exception:
                account_data[addr]['balance'] = 'NAN'
                account_data[addr]['total-balance'] = sum([x for x in account_data[addr].values() if isinstance(x, Decimal)])
                err = {'error': f'error parsing balance output for {addr}',
                       'reply': balance}
                logger.debug(json.dumps(err, sort_keys = True, indent = 4))
        else:
            account_data[addr]['balance'] = 'NAN'
            account_data[addr]['total-balance'] = sum([x for x in account_data[addr].values() if isinstance(x, Decimal)])
            err = {'error': f'unable to fetch balance for {addr} after {retries} tries'}
            logger.debug(json.dumps(err, sort_keys = True, indent = 4))

    with open(output_file, 'w', encoding = 'utf8') as f:
        field_names = ['Address', 'Balance', 'Delegations', 'Undelegations', 'Rewards', 'Total']
        writer = csv.writer(f)
        writer.writerow(field_names)
        for k, v in account_data.items():
            formatted_result = [k, v['balance'], v['total-delegations'], v['total-undelegations'], v['total-rewards'], v['total-balance']]
            writer.writerow(formatted_result)

def create_validator_snapshot(block_num, endpoint, output_file, retries):
    v_print(f'[get_validator_snapshot] Block Num: {block_num}')
    logger = logging.getLogger('validator')
    logger.setLevel(logging.DEBUG)

    all_validator_information = defaultdict(dict)
    all_validators = get_all_validators_addresses(endpoint, retries)
    if all_validators is not None:

        pool = ThreadPool()
        threads = []
        for v in all_validators:
            threads.append(pool.apply_async(get_validator_information_by_block, (v, block_num, endpoint, retries)))

        for t in threads:
            addr, info = t.get()
            # Don't print if address not found
            if info is not None:
                try:
                    all_validator_information[addr]['lifetime-reward'] = info['lifetime']['reward-accumulated']
                    info['blockNumber'] = block_num
                    logger.debug(json.dumps(info, sort_keys = True, indent = 4))
                except Exception:
                    err = {'error': f'error parsing validator information for {addr} for block #{block_num}'}
                    logger.debug(json.dumps(err, sort_keys = True, indent = 4))
    else:
        err = {'error': f'unable to fetch list of all validators after for block #{block_num} after {retries} tries'}
        logger.debug(json.dumps(err, sort_keys = True, indent = 4))

    with open(output_file, 'w', encoding = 'utf8') as f:
        field_names = ['Address', 'Lifetime Rewards']
        writer = csv.writer(f)
        writer.writerow(field_names)
        for k, v in account_data.items():
            formatted_result = [k, v['lifetime-reward']]
            writer.writerow(formatted_result)

def get_epoch_last_block(epoch, blocks_per_epoch):
    return ((epoch + 1) * blocks_per_epoch) - 1

def get_epoch_first_block(epoch, blocks_per_epoch):
    return epoch * blocks_per_epoch

def init_loggers():
    # Log to dump all blocks in chain
    logger = logging.getLogger('blockchain')
    logger.addHandler(get_simple_rotating_log_handler(block_log))

    # Log to dump all RPC results from account snapshots
    logger = logging.getLogger('rpc')
    logger.addHandler(get_simple_rotating_log_handler(rpc_log))

    # Log to dump all RPC results from validator snapshots
    logger = logging.getLogger('validator')
    logger.addHandler(get_simple_rotating_log_handler(validator_log))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('endpoint', help = 'Endpoint to query for blockchain data')
    parser.add_argument('--retries', default = 5, help = 'Number of retries for a request before failing')
    parser.add_argument('--delay', default = 30, type = int, help = 'Delay between iterations in seconds')
    parser.add_argument('--verbose', default = False, action = 'store_true', help = 'Verbose print for debug')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    network_accounts = set()
    prev_epoch = 0
    prev_block = 0

    blocks_per_epoch = 0
    metadata = get_node_metadata(args.endpoint, args.retries)
    try:
        blocks_per_epoch = metadata['blocks-per-epoch']
    except Exception as e:
        print("Error getting blocks_per_epoch. Check network status?")
        exit()
    v_print(f'Blocks Per Epoch: {blocks_per_epoch}')

    # NOTE: Should not fail
    if not path.exists(data):
        os.mkdir(data)
    else:
        # Read last existing accounts file for epoch & active network accounts
        account_files = glob(path.join(data, 'accounts*.csv'))
        if len(account_files) > 0:
            # Might need to use min to get latest file
            latest_account_file = max(account_files, key = path.getctime)
            v_print(f'Reading initial data from: {latest_account_file}')
            with open(latest_account_file, 'r', encoding = 'utf8') as f:
                reader = csv.reader(f)
                # Skip header line
                next(reader)
                for line in reader:
                    network_accounts.add(line[0].strip())
            try:
                epoch_token = path.basename(latest_account_file).split('.')[0].split('_')[1]
                prev_epoch = int(epoch_token)
                # Since account filed generated, all blocks in that epoch should have been fetched
                prev_block = get_epoch_first_block(int(epoch_token) + 1, blocks_per_epoch)
            except Exception:
                pass

    # Create loggers after creating data directory
    init_loggers()

    while True:
        v_print(f'-- Loop {datetime.now()}--')
        # Don't retry latest block, just skip iteration
        latest_block = get_latest_header(args.endpoint)
        if latest_block is not None:
            try:
                current_block = latest_block['blockNumber']
                current_epoch = latest_block['epoch']
            except:
                # Latest block RPC failed, skip iteration
                current_block = prev_block
                current_epoch = prev_epoch
                pass

            v_print(f'[main] Current Block: {current_block}')
            v_print(f'[main] Previous Block: {prev_block}')

            # Log blockchain activity
            if current_block > prev_block:
                active_addresses = get_blockchain(prev_block, current_block, args.endpoint, args.retries)
                network_accounts.update(active_addresses)
                prev_block = current_block

                v_print(f'[main] Num Active Accounts: {len(active_addresses)}')
                v_print(f'[main] Num Total Accounts: {len(network_accounts)}')


            v_print(f'[main] Current Epoch: {current_epoch}')
            v_print(f'[main] Previous Epoch: {prev_epoch}')

            # Do snapshot on epoch change
            if current_epoch > prev_epoch:
                prev_epoch = current_epoch - 1
                epoch_last_block = get_epoch_last_block(prev_epoch, blocks_per_epoch)

                v_print(f'[main] Last block of epoch {prev_epoch}: {epoch_last_block}')

                account_file = path.join(data, f'accounts_{prev_epoch}.csv')
                # Check if output already exists, to not overwrite it
                if path.exists(account_file):
                    if os.stat(account_file).st_size > 0:
                        v_print(f'[main] Account snapshot file already exists & is not empty: {account_file}')
                    else:
                        v_print(f'[main] Account snapshot file already exists & is empty: {account_file}')
                        create_account_snapshot(network_accounts, epoch_last_block, prev_epoch, args.endpoint, account_file, args.retries)
                else:
                    create_account_snapshot(network_accounts, epoch_last_block, prev_epoch, args.endpoint, account_file, args.retries)

                validator_file = path.join(data, f'validators_{prev_epoch}.csv')
                if path.exists(validator_file):
                    if os.stat(validator_file).st_size > 0:
                        v_print(f'[main] Validator snapshot file already exists & is not empty: {validator_file}')
                    else:
                        v_print(f'[main] Validator snapshot file already exists & is empty: {validator_file}')
                        create_validator_snapshot(epoch_last_block, args.endpoint, validator_file, args.retries)
                else:
                    create_validator_snapshot(epoch_last_block, args.endpoint, validator_file, args.retries)

                prev_epoch = current_epoch

        else:
            v_print('[main] LatestHeader failed')
        # Sleep between iterations, allow for catch up time
        sleep(args.delay)
