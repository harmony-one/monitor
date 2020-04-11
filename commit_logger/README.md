### Commit Logger

Track Network version deployed & longevity

#### Requirements
`python3 -m pip install -r requirements.txt`

#### Setup
To generate sample input file `network_information.txt` in the root directory, run:
```
python3 commit_logger.py --setup
```
Do not change the name of the file or move the file.
Sample is generated with Mainnet as the example.

Generated sample:
```
# network name, rpc endpoint
mainnet, https://api.s0.t.hmny.io
mainnet, https://api.s1.t.hmny.io
mainnet, https://api.s2.t.hmny.io
mainnet, https://api.s3.t.hmny.io
```

Warning: Having too many request targets in the config_file might cause "too many files" errors for the requests.

#### Run data collection
```
python3 commit_logger.py
```

#### Run flask server for JSON webpage
```
export FLASK_APP=commit_log
python3 -m flask run
```

Give the `-p [PORT]` parameter to specify the port for the server.

#### Output
```
./data/commit.json
./data/commit_*.log
```

Can also see the JSON output displayed on http://localhost:5000/commit_log (Replace 5000 with the port specified if different)

Or using `curl`:
```json
$ curl http://localhost:5000/commit_log | jq
{
    "ostn": {
        "Harmony (C) 2020. harmony, version v5826-v1.9.1-12-g030eaaf4 (leochen@ 2020-04-09T23:48:17+0000)": {
            "0": {
                "block-height": "9545",
                "first-block-timestamp": "04/09_22:10:37",
                "latest-timestamp": "04/10_20:08:48"
            },
            "1": {
                "block-height": "9449",
                "first-block-timestamp": "",
                "latest-timestamp": "04/10_20:08:55"
            },
            "2": {
                "block-height": "9550",
                "first-block-timestamp": "04/09_22:10:42",
                "latest-timestamp": "04/10_20:08:46"
            },
            "3": {
                "block-height": "9538",
                "first-block-timestamp": "04/09_23:11:21",
                "latest-timestamp": "04/10_20:08:53"
            }
        }
    }
}
```
