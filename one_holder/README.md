### Delegator Leaderboard

Track delegator rewards for P3 campaign

#### Requirements
`python3 -m pip install -r requirements.txt`

#### Run data collection using a Cron job
Open list of Cron jobs using `sudo crontab -e`
To run hourly, add `0 * * * * python3 /path/to/script/get_delegation_info.py`

#### Run flask server
```
export FLASK_APP=delegator
python3 -m flask run
```

Give the `-p [PORT]` parameter to specify the port for the server.
Flask uses port 5000 by default

#### Output
```
./data/delegator_rewards.html
./csv/...
```

HTML page: http://localhost:5000/delegators
