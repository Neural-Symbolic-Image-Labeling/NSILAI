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
    MONGO_URI='mongodb://localhost:27017/NISL'
)

mongo = PyMongo(app)

@app.route('/flaskadmin/pretrainedmodel', methods=['GET'])
def input_image():
    return render_template("input_image.html")


@app.route('/flaskadmin/pretrain', methods=['GET'])
def pretrain():
    image_id = request.args.get('_id')
    # base64_img_bytes = image_id.encode('utf-8')
    target = mongo.db.image.find_one({'_id': image_id})
    if target is None:
        return 'No image found!'
    base64_img_bytes = target.data
    base64_img = base64_img_bytes[base64_img_bytes.rfind(','):]

    decoded_image_data = base64.b64decode(base64_img)
    # bin_im = "".join(["{:08b}".format(x) for x in decoded_image_data])

    # Run pretrained model
    json_res = pretrain_label(decoded_image_data)

    # Saving the output json to specific image
    target.interpretation = json_res

    return render_template('showgallery.html', image=[target])








@app.route('/flaskadmin')
def mainpage():
    return render_template("index.html")
