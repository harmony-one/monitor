import argparse
import json
import os

from decimal import Decimal

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

    validator_information_file = os.path.join(args.data_path, 'shard0', 'validator_info_per_epoch.txt')
    with open(validator_information_file, 'r') as f:
        v_print(f'Reading validator information from: {validator_information_file}')
        validator_data = json.load(f)

    validator_info = {}
    for epoch, validators in validator_data.items():
        v_print(f'Pruning validator information: {epoch}')
        validator_info[epoch] = {}
        for v in validators:
            pruned_validator = {
                'bls-keys': v['validator']['bls-public-keys'],
                'total-stake': v['total-delegation'],
                'delegations': [x for x in v['validator']['delegations'] if x['amount'] != 0 or x['delegator-address'] == v['validator']['address']],
                'rate': v['validator']['rate']
            }
            pruned_validator['stake-per-key'] = str(Decimal(pruned_validator['total-stake']) / len(pruned_validator['bls-keys']))
            validator_info[epoch][v['validator']['address']] = pruned_validator

    print(f'Dumping pruned validator data: {args.data_path}')
    with open(os.path.join(os.getcwd(), args.data_path, 'shard0', 'pruned_validator_info.txt'), 'w') as f:
        json.dump(validator_info, f)
