from flask import Flask
import os

app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nsil pog')

import views
