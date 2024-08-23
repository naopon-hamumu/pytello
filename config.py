import os

from flask import Flask

WEB_ADDRESS = '0.0.0.0'
WEB_PORT = 5000
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # 引数で指定したパスの絶対パスを返す
TEMPLATES = os.path.join(PROJECT_ROOT, 'droneapp/templates')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'droneapp/static')
DEBUG = False
LOF_FILE = 'ptell.log'

app = Flask(__name__, template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

if DEBUG:
    app.debug = DEBUG
