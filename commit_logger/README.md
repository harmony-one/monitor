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
