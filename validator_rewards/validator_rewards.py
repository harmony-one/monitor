import argparse
import json

from pyhmy import (
    get_all_validator_addresses,
    get_validator_information
)

def get_block_by_num(block_num, endpoint):
    params = [
        str(hex(block_num)),
        False,
    ]
    payload = {
        "id": "1",
        "jsonrpc": "2.0",
        "method": "hmy_getBlockByNumber",
        "params": params
    }
    headers = {
        'Content-Type': 'application/json'
    }
    timeout = 5
    try:
        resp = requests.request('POST', endpoint, headers=headers, data=json.dumps(payload),
                                timeout=timeout, allow_redirects=True)
        return json.loads(resp.content)
    except Exception as e:
        v_print(f'{e.__class__}: {e}')
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=int, help="First block")
    parser.add_argument("--end", required=True, type=int, help="Last block")
    parser.add_argument("--endpoint", default="http://localhost:9500", help="Endpoint to query")
    parser.add_argument("--verbose", action='store_true', help="Verbose print for debug")

    args = parser.parse_args()

    if args.verbose:
        def v_print(*args, **kwargs):
            print(*args, **kwargs)
    else:
        def v_print(*args, **kwargs):
            return

    block_timestamps = []
    block_tx = []
    block_stx = []
    for block_num in range(args.start, args.end):
        v_print(f'Block {block_num}/{args.end}', end="\r")
        reply  = get_block_by_num(block_num, args.endpoint)
        try:
            block_timestamps.append(int(reply['result']['timestamp'], 0))
            block_tx.append(len(reply['result']['transactions']))
            block_stx.append(len(reply['result']['stakingTransactions']))
        except Exception as e:
            v_print(f'{e.__class__}: {e}')
            pass

    block_times = [y - x for x, y in zip(block_timestamps, block_timestamps[1:])]
    avg = sum(block_times) / len(block_times)
    print(f'Average Block Time: {avg}')

    unique_times = Counter(block_times)
    print(f'Unique block times: {unique_times.most_common()}')

    # offset = [0].extend(block_times)
