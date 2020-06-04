from flask import (
    render_template,
)
from app import app

@app.route('/fn_earnings')
def fn_earnings():
    html = ''
    with open('index.html', 'r') as f:
        for line in f:
            html = html + line.strip()
    return html
