### FN Earning Page

#### Requirements
To install dependencies:
```
python3 -m pip install -r requirements.txt
```

#### Generate static HTML page
Provide CSV file with data
```
python3 generate_html.py --input [csv_file]
```

#### Start Server
```
export FLASK_APP=earnings
python3 -m flask run
```   
