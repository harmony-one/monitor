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
    parser.add_argument('--start-block', type=int, required=True, help='Block to start from')
    parser.add_argument('--end-block', type=int, required=True, help='Block to end on')
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

    blocks_per_epoch = defaultdict(list)
    signers_per_block = {}
    block = args.start_block
    for x in range(args.start_block, args.end_block + 1):
        v_print(f'Getting block signers: {x}/{args.end_block}\r')
        block_data = blockchain.get_block_by_number(x, endpoint=args.endpoint)
        signers = blockchain.get_block_signer_keys(x, endpoint=args.endpoint)

        epoch = int(block_data['epoch'], 0)
        blocks_per_epoch[epoch].append(x)

        signers_per_block[x] = signers

    v_print(f'Dumping data to files: {args.output_dir}')
    with open(os.path.join(os.getcwd(), args.output_dir, 'blocks_per_epoch.txt'), 'w') as f:
        json.dump(blocks_per_epoch, f)

    with open(os.path.join(os.getcwd(), args.output_dir, 'signers_per_block.txt'), 'w') as f:
        json.dump(signers_per_block, f)
