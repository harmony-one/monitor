import argparse
import json
import os

from pyhmy import (
    blockchain,
    staking
)

def last_block_before_epoch(epoch_num, bpe):
    return (epoch_num) * bpe - 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-epoch', type=int, help='Epoch to start with, must be at least 1')
    parser.add_argument('--end-epoch', type=int, help='Epoch to end on')
    parser.add_argument('--output-dir', help='Path to directory to output data to')
    parser.add_argument('--endpoint', default='http://localhost:9500', help='Endpoint to query, default localhost')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    blocks_per_epoch = blockchain.get_node_metadata(endpoint=args.endpoint)['blocks-per-epoch']

    validator_info_by_epoch = {}
    for x in range(args.start_epoch, args.end_epoch + 1):
        block_before = last_block_before_epoch(x, blocks_per_epoch)
        v_print(f'Getting validator information: {block_before} {x}/{args.end_epoch}\r')
        validator_info = staking.get_all_validator_information_by_block(block_before, endpoint=args.endpoint)

        validator_info_by_epoch[x] = validator_info

    v_print(f'Dumping data to files: {args.output_dir}')
    with open(os.path.join(os.getcwd(), args.output_dir, 'validator_info_per_epoch.txt'), 'w') as f:
        json.dump(validator_info_by_epoch, f)
