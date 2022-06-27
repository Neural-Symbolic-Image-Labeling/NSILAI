from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
# CORS
cors = CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})
# configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nsil pog')

import views
