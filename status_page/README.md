### Status Page
Network Status Page

#### Requirements
To install dependencies:
```
python3 -m pip install -r requirements.txt
```

#### Configuration File
To monitor other networks, edit the `networks.txt` file.
NOTE: Changing the `networks.txt` while running the server will update immediately.

#### Authentication File
Run `scripts/setup.sh` to generate the initial `watchdog_authentication.txt`.
Replace `username` with the correct username & `password` with the correct password.

#### Start Server
```
export FLASK_APP=status
python3 -m flask run
```   
