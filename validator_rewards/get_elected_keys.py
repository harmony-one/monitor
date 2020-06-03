import argparse
import json
import os

from collections import (
    defaultdict
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True, help='Path to data files')
    parser.add_argument('--num-shards', default=4, type=int, help='Number of shards')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    internal_keys = []
    elected_keys = defaultdict(list)

    for x in range(0, args.num_shards):
        validator_key_file = os.path.join(args.data_path, f'shard{x}', 'validators_per_epoch.txt')
        with open(validator_key_file, 'r') as f:
            validator_keys = json.load(f)

        for e in validator_keys:
            if e == '2':
                internal_keys.extend(validator_keys['2'])
            elected_keys[e].extend([x for x in validator_keys[e] if x not in internal_keys])

    print(f'Dumping elected validator information.')
    with open(os.path.join(os.getcwd(), args.data_path, 'elected_validators.txt'), 'w') as f:
        json.dump(elected_keys, f)

    print(f'Dumping internal key list.')
    with open(os.path.join(os.getcwd(), args.data_path, 'internal_keys.txt'), 'w') as f:
        json.dump(internal_keys, f)
