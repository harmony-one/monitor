import argparse
import csv
import json
import os

from collections import (
    defaultdict
)

from decimal import (
    Decimal
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True, help='Path to data files')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    committee_info_file = os.path.join(args.data_path, 'committee.txt')
    with open(committee_info_file, 'r') as f:
        committee_info = json.load(f)

    rewards_file = os.path.join(args.data_path, 'rewards_0.txt')
    with open(rewards_file, 'r') as f:
        reward_per_key = json.load(f)

    key_address = defaultdict(str)
    total_reward_per_key = {}
    for k, r in reward_per_key.items():
        v_print(f'Key {k}')
        total_reward_per_key[k] = sum(Decimal(x) for x in r)
        for epoch, comm in committee_info.items():
            if comm:
                for x in comm['keys']:
                    if x['key'] == k:
                        key_address[k] = x['address']
                        break
            if key_address[k]:
                break

    v_print(f'Dumping total reward data per key')
    with open(os.path.join(os.getcwd(), args.data_path, 'rewards.csv'), 'w') as f:
        out = csv.writer(f)
        out.writerow(['Address', 'Key', 'Reward'])
        for k, r in total_reward_per_key.items():
            a = key_address[k]
            out.writerow([a, k, r])
