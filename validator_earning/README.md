### Validator Earning

Track validator stats & earnings

#### Requirements
`python3 -m pip install -r requirements.txt`


#### Run data collection
```
python3 validator_earning.py --network_endpoint {os, ps, stn}
```

#### Run flask server for JSON webpage
```
export FLASK_APP=earning
python3 -m flask run
```

Give the `-p [PORT]` parameter to specify the port for the server.
Flask uses port 5000 by default

#### Output
```
./data/earning.html
./data/network_stats.json
./data/validator_info.json
```

HTML page: http://localhost:5000/validators
Query JSON for specific address: http://localhost:5000/valiators?address=[ONE_ADDRESS]
Query JSON for network stats: https://localhost:5000/validators?stats=true
** Replace 5000 above with the port if specified a different port
