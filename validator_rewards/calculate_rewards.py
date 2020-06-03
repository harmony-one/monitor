import argparse
import json
import os

from collections import (
    defaultdict
)

from decimal import (
    Decimal
)

from glob import (
    glob
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True, help='Path to data files')
    parser.add_argument('--num-shards', default=4, help='Number of shards')
    parser.add_argument('--verbose', action='store_true', help='Verbose')

    args = parser.parse_args()

    if args.verbose:
        def v_print(s):
            print(s)
    else:
        def v_print(s):
            return

    validator_info_file = os.path.join(args.data_path, 'shard0', 'pruned_validator_info.txt')
    with open(validator_info_file, 'r') as f:
        validator_info = json.load(f)

    committee_info_file = os.path.join(args.data_path, 'committee.txt')
    with open(committee_info_file, 'r') as f:
        committee_info = json.load(f)

    internal_keys_file = os.path.join(args.data_path, 'internal_keys.txt')
    with open(internal_keys_file, 'r') as f:
        internal_keys = json.load(f)

    key_rewards = defaultdict(list)

    for s in range(args.num_shards):
        v_print(f'Shard {s}')
        block_signers = {}
        block_signer_files = glob(os.path.join(args.data_path, f'shard{s}', 'signers_per_block*.txt'))
        for f in block_signer_files:
            with open(f, 'r') as rf:
                all_block_signers = json.load(rf)
            for block, signers in all_block_signers.items():
                block_signers[block] = [i for i in signers if i not in internal_keys]

        block_epoch_data_file = glob(os.path.join(args.data_path, f'shard{s}', 'pruned_block_data.txt'))[0]
        with open(block_epoch_data_file, 'r') as f:
            blocks_per_epoch = json.load(f)

        for e in blocks_per_epoch.keys():
            if e == '1' or e == '2':
                continue
            v_print(f'Epoch {e}')
            for b in range(blocks_per_epoch[e]['start'], blocks_per_epoch[e]['end'] + 1):
                print(f'Block {b}\r')
                keys = committee_info[e]['keys']
                total_eff_stake = sum(Decimal(keys[i]['eff-stake']) for i in range(len(keys)) if keys[i]['key'] in block_signers[str(b)])
                for k in block_signers[str(b)]:
                    k_data = [keys[x] for x in range(len(keys)) if keys[x]['key'] == k][0]
                    reward = 28 * Decimal(k_data['eff-stake']) / total_eff_stake
                    self_reward = reward * Decimal(k_data['self-stake-percent'])
                    commission = (reward - (self_reward)) * Decimal(k_data['rate'])
                    key_rewards[k].append(str(self_reward + commission))

    v_print(f'Dumping reward data per key')
    with open(os.path.join(os.getcwd(), args.data_path, 'rewards_0.txt'), 'w') as f:
        json.dump(key_rewards, f)
