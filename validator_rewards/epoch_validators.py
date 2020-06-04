import argparse
import json
import os

from collections import (
    defaultdict
)

from pyhmy import (
    blockchain
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-epoch', type=int, required=True, help='Epoch to start from')
    parser.add_argument('--end-epoch', type=int, required=True, help='Epoch to end on')
    parser.add_argument('--endpoint', default='http://localhost:9500', help='Endpoint the query, default localhost')
    parser.add_argument('--output-dir', help='Path to directory to output data to')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    validators_per_epoch = {}
    for x in range(args.start_epoch, args.end_epoch + 1):
        v_print(f'Getting validators: {x}/{args.end_epoch}\r')
        keys = blockchain.get_validator_keys(x, endpoint=args.endpoint)
        validators_per_epoch[x] = keys

    v_print(f'Dumping data to files: {args.output_dir}')
    with open(os.path.join(os.getcwd(), args.output_dir, 'validators_per_epoch.txt'), 'w') as f:
        json.dump(validators_per_epoch, f)
