from flask import *
from flask_cors import CORS
from flask_pymongo import PyMongo
import base64
from views.pretrain import pretrain_label

import os

app = Flask(__name__)
# CORS
cors = CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})
# configuration
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nsil pog')

app.config.update(
    MONGO_HOST='localhost',
    MONGO_PORT=27017,
    MONGO_URI='mongodb://localhost:27017/flask'
)

mongo = PyMongo(app)

@app.route('/flaskadmin/pretrainedmodel', methods=['GET'])
def input_image():
    return render_template("input_image.html")


@app.route('/flaskadmin/pretrain', methods=['GET'])
def pretrain():
    image_url = request.args.get('URL')
    base64_img_bytes = image_url.encode('utf-8')
    decoded_image_data = base64.b64decode(base64_img_bytes)
    bin_im = "".join(["{:08b}".format(x) for x in decoded_image_data])
    json_res = pretrain_label(bin_im)





@app.route('/flaskadmin')
def mainpage():
    return render_template("index.html")
