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
      "0": 9249,
      "1": 9154,
      "2": 9258,
      "3": 9243,
      "first-block-timestamp": "04/10_05:05:37",
      "latest": "04/11_02:02:19"
    }
  },
  "ps": {
    "Harmony (C) 2020. harmony, version v5726-v1.3.5-35-gfb4dabed (ec2-user@ 2020-03-25T08:53:25+0000)": {
      "0": 180839,
      "1": 180843,
      "first-block-timestamp": "03/25_08:08:15",
      "latest": "04/11_02:02:13"
    }
  },
  "stn": {
    "Harmony (C) 2020. harmony, version v5826-v1.3.5-135-g030eaaf4 (ec2-user@ 2020-04-08T19:40:01+0000)": {
      "0": 5992,
      "1": 6005,
      "first-block-timestamp": "04/10_13:01:04",
      "latest": "04/11_02:02:15"
    }
  }
}
```
