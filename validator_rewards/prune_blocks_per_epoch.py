import argparse
import json
import os

from collections import defaultdict
from glob import glob

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

    for x in range(args.num_shards):
        blocks_per_epoch = defaultdict(dict)

        blocks_per_epoch_files = glob(os.path.join(args.data_path, f'shard{x}', 'blocks_per_epoch*.txt'))
        for b in blocks_per_epoch_files:
            with open(b, 'r') as f:
                v_print(f'Reading block information from: {b}')
                epoch_block_data = json.load(f)
            for epoch, blocks in epoch_block_data.items():
                if blocks_per_epoch[epoch]:
                    blocks_per_epoch[epoch] = {
                        'start': min(blocks),
                        'end':blocks_per_epoch[epoch]['end']
                    }
                else:
                    blocks_per_epoch[epoch] = {
                        'start': min(blocks),
                        'end': max(blocks)
                    }

        print(f'Dumping pruned block data: {args.data_path}')
        with open(os.path.join(os.getcwd(), args.data_path, f'shard{x}', 'pruned_block_data.txt'), 'w') as f:
            json.dump(blocks_per_epoch, f, sort_keys=True)
