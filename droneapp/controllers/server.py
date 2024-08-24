import logging
from flask import render_template
import config

logger = logging.getLogger(__name__)
app = config.app

@app.route('/')
def index():
    return render_template('index.html')

def run():
    app.run(host=config.WEB_ADDRESS, port=config.WEB_PORT, threaded=True)
