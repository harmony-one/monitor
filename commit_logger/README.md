### Commit Logger

#### Requirements
`python3 -m pip install -r requirements.txt`

#### Run commands
Using a Tmux session, run the logger:
```
python3 commit_logger.py --endpoints [https://api.s0.b.hmny.io,...]
```
Split into 2 panes & run the flask server:
```
export FLASK_APP=commit_log
python3 -m flask run -p [port]
```

#### Output
```
./data/commit.json
./data/commit_*.log
```
