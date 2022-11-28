
from flask_cors import CORS
from flask import Flask

app = Flask(__name__,template_folder='tpl')
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/index": {"origins": "http://localhost"}})

from app import app_routes

