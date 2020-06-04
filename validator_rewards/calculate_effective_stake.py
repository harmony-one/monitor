import argparse
import json
import os

from collections import (
    defaultdict
)

from decimal import (
    Decimal
)

from statistics import (
    median
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True, help='Path to data files')
    parser.add_argument('--end-epoch', required=True, type=int, help='Epoch to end on')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    validator_data_file = os.path.join(args.data_path, 'shard0', 'pruned_validator_info.txt')
    with open(validator_data_file, 'r') as f:
        validator_info = json.load(f)

    elected_key_file = os.path.join(args.data_path, 'elected_validators.txt')
    with open(elected_key_file, 'r') as f:
        elected_keys = json.load(f)

    committee = {}
    for x in range(2, args.end_epoch + 1):
        v_print(f'Epoch {x}')
        committee[x] = {}
        committee_keys = []
        for a, v in validator_info[str(x)].items():
            self_delegation = Decimal([d['amount'] for d in v['delegations'] if d['delegator-address'] == a][0])
            total_delegation = sum(Decimal(d['amount']) for d in v['delegations'])
            for k in v['bls-keys']:
                if k in elected_keys[str(x)]:
                    committee_keys.append((k, v['stake-per-key'], a, v['rate'], self_delegation / total_delegation))

        if len(committee_keys) > 0:
            total_stake = sum(Decimal(i[1]) for i in committee_keys)
            median_stake = median(Decimal(i[1]) for i in committee_keys)

            committee[x]['total-stake'] = str(total_stake)
            committee[x]['median-stake'] = str(median_stake)

            committee[x]['keys'] = []
            for k in committee_keys:
                eff_stake = max(median_stake * Decimal(.85), min(median_stake * Decimal(1.15), Decimal(k[1])))
                committee[x]['keys'].append({
                    'address': k[2],
                    'key': k[0],
                    'eff-stake': str(eff_stake),
                    'self-stake-percent': str(k[4]),
                    'rate': k[3],
                })

    print(f'Dumping effective stake calculations.')
    with open(os.path.join(os.getcwd(), args.data_path, 'committee.txt'), 'w') as f:
        json.dump(committee, f)
