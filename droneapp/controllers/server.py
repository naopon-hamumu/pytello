import logging
import config

logger = logging.getLogger(__name__)
app = config.app

@app.route('/')
def index():
    return "Hello World!"

def run():
    app.run(host=config.WEB_ADDRESS, port=config.WEB_PORT, threaded=True)
    