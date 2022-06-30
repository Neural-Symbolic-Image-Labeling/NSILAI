from flask import *
from flask_cors import CORS
from flask_pymongo import PyMongo
import base64
from views.pretrain import pretrain_label
from views.foil import foil

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
    # Only for testing
    # image = {'_id': '123', 'name': 'test',
    #          'data': 'data:/image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAA' \
    #         'LEwEAmpwYAAAB1klEQVQ4jY2TTUhUURTHf+fy/HrjhNEX2KRGiyIXg8xgSURuokX' \
    #         'LxFW0qDTaSQupkHirthK0qF0WQQQR0UCbwCQyw8KCiDbShEYLJQdmpsk3895p4aS' \
    #         'v92ass7pcfv/zP+fcc4U6kXKe2pTY3tjSUHjtnFgB0VqchC/SY8/293S23f+6VEj' \
    #         '9KKwCoPDNIJdmr598GOZNJKNWTic7tqb27WwNuuwGvVWrAit84fsmMzE1P1+1TiK' \
    #         'MVKvYUjdBvzPZXCwXzyhyWNBgVYkgrIow09VJMznpyebWE+Tdn9cEroBSc1JVPS+' \
    #         '6moh5Xyjj65vEgBxafGzWetTh+rr1eE/c/TMYg8hlAOvI6JP4KmwLgJ4qD0TIbli' \
    #         'TB+sunjkbeLekKsZ6Zc8V027aBRoBRHVoduDiSypmGFG7CrcBEyDHA0ZNfNphC0D' \
    #         '6amYa6ANw3YbWD4Pn3oIc+EdL36V3od0A+MaMAXmA8x2Zyn+IQeQeBDfRcUw3B+2' \
    #         'PxwZ/EdtTDpCPQLMh9TKx0k3pXipEVlknsf5KoNzGyOe1sz8nvYtTQT6yyvTjIax' \
    #         'smHGB9pFx4n3jIEfDePQvCIrnn0J4B/gA5J4XcRfu4JZuRAw3C51OtOjM3l2bMb8' \
    #         'Br5eXCsT/w/EAAAAASUVORK5CYII=',
    #          'interpretation': []}
    # mongo.db.image.insert_one(image)

    return render_template("input_image.html")

# @app.route('/flaskadmin/pretrain/<id>', methods=['GET'])
# def pretrain(id):
# Post
#return status

@app.route('/flaskadmin/pretrain', methods=['GET'])
def pretrain():
    image_id = request.args.get('_id')
    # base64_img_bytes = image_id.encode('utf-8')
    target = mongo.db.image.find_one({'_id': image_id})
    if target is None:
        return 'No image found!'
    base64_img_bytes = target['data']
    base64_img = base64_img_bytes[base64_img_bytes.rfind(','):]

    decoded_image_data = base64.b64decode(base64_img)
    # bin_im = "".join(["{:08b}".format(x) for x in decoded_image_data])

    # Run pretrained model
    # json_res = pretrain_label(decoded_image_data)

    # Saving the output json to specific image
    # data = json.load(json_res)

    # For testing
    data = pretrain_label(decoded_image_data)
    # data = json.load(data)
    interpretation = {k: data[0][k] for k in ['object', 'overlap'] if k in data[0]}
    # print(interpretation)
    new_int = { '$set': {'interpretation': interpretation}}
    mongo.db.image.update_one(target, new_int)

    return render_template('showgallery.html', target=target)


@app.route('/flaskadmin/selectset', methods=['GET'])
def select_set():
    return render_template('selectset.html')


# Classification
@app.route('/flaskadmin/foil', methods=['POST'])
def train_rule():
    # set_name = request.args.get('set')
    body = request.get_json()
    wrksp = mongo.db.Workspance.find_one({'_id': body['workspaceID']})
    target_collect = {}
    for collect in wrksp['collections']:
        if collect['_id'] == body['collectionID']:
            target_collect = collect
    if target_collect is {}:
        return 'No such image collection!'

    image_metas = target_collect['images']
    lst = []
    index = 1
    # Add condition for no label
    for img in image_metas:
        img_init = mongo.db.image.find_one({'_id': img['imageId']})
        img_dict = {'imageID': index, 'type': img['labels'][0], 'object': img_init['interpretation']['object'],
                    'overlap': img_init['interpretation']['overlap']}
        lst.append(img_dict)
        index += 1

    rule = foil(lst)
    # Need to return a label name or several label name

    # target_rule = target_collect['rules']

    for res in rule:
        flag = 0
        for rules in target_collect['rules']:
            if res['name'] == rules['label']:
                rules['value'] == res['value']
                flag = 1
        if flag == 0:
            target_collect['rules'].append({'label': res['name'],
                                            'value': res['value']})

    # if target_rule is []:
    #     rule = {
    #         'label': '', # label need to be added
    #         'value': rule,
    #     }, {'_id': 'false'}
    #     target_rule.append(rule)
    # else:
    #     new_rule = {'$set': {'value': rule}}
    #     target_rule.append(new_rule)

    return render_template('Success.html', target=target_collect['rules'])


@app.route('/flaskadmin')
def mainpage():
    return render_template("index.html")
