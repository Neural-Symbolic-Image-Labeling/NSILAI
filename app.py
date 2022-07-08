from flask import *
from flask_cors import CORS
from flask_pymongo import PyMongo
import base64
from views.pretrain import pretrain_label
from views.foil import FOIL

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


# @app.route('/flaskadmin/pretrainedmodel', methods=['GET'])
# def input_image():
#
#     return render_template("input_image.html")

# @app.route('/flaskadmin/pretrain/<id>', methods=['GET'])
# def pretrain(id):
# Post
# return status

# @app.route('/flaskadmin/pretrain', methods=['GET'])
@app.route('/flaskadmin/pretrain/<img_id>', methods=['POST'])
def pretrain(img_id):
    # image_id = request.args.get('_id')
    # base64_img_bytes = image_id.encode('utf-8')
    target = mongo.db.image.find_one({'_id': img_id})
    if target is None:
        return {'code': 2,
                'msg': 'No such image, id is invalid!',
                'errorLog': None
                }
    base64_img_bytes = target['data']
    base64_img = base64_img_bytes[base64_img_bytes.rfind(','):]

    decoded_image_data = base64.b64decode(base64_img)
    # bin_im = "".join(["{:08b}".format(x) for x in decoded_image_data])

    # Run pretrained model
    # json_res = pretrain_label(decoded_image_data)

    # Saving the output json to specific image
    # data = json.load(json_res)

    # For testing
    try:
        data = pretrain_label(decoded_image_data)
    except Exception as err:
        return {'code': 3,
                'msg': 'ERROR in pre-train',
                'errorLog': err
                }

    # data = json.load(data)
    interpretation = {k: data[0][k] for k in ['object', 'overlap'] if k in data[0]}
    # print(interpretation)
    new_int = {'$set': {'interpretation': interpretation}}
    try:
        mongo.db.image.update_one(target, new_int)
    except Exception as err:
        return {'code': 2,
                'msg': 'Fail to Update!',
                'errorLog': err
                }

    return {'code': 0, 'msg': "success", 'errorLog': None}


# @app.route('/flaskadmin/selectset', methods=['GET'])
# def select_set():
#     return render_template('selectset.html')


# Classification
@app.route('/flaskadmin/foil', methods=['POST'])
def train_rule():
    body = request.get_json()
    wrksp = mongo.db.Workspance.find_one({'_id': body['workspaceID']})
    if wrksp is None:
        return {'code': 2,
                'msg': 'No such workspace!',
                'errorLog': None
                }
    target_collect = None

    for collect in wrksp['collections']:
        if collect['_id'] == body['collectionID']:
            target_collect = collect
    if target_collect is None:
        return {'code': 2,
                'msg': 'No such image collection!',
                'errorLog': None
                }

    image_metas = target_collect['images']
    if image_metas is []:
        return {'code': 2,
                'msg': 'No images in the collection!',
                'errorLog': None
                }
    lst = []
    index = 1
    # Add condition for no label
    for img in image_metas:
<<<<<<< HEAD
        img_init = mongo.db.image.find_one({'_id': img['imageId']})
        if not len(img['labels']) == 0:
            img_dict = {'imageID': index, 'type': img['labels'][0], 'object': img_init['interpretation']['object'],
                        'overlap': img_init['interpretation']['overlap']}
            lst.append(img_dict)
            index += 1
    try:
        rule = FOIL(lst)
    except Exception as ex:
        return {'code': 4,
                'msg': 'ERROR in FOIL',
                'errorLog': ex
                }

    for key in rule:
        flag = 0
        if not target_collect['rules']:
            target_collect['rules'].append({'label': key, 'value': rule[key]})
        else:
            for rules in target_collect['rules']:
                if key == rules['label']:
                    rules['value'] = rule[key]
                    flag = 1
            if flag == 0:
                target_collect['rules'].append({'label': key, 'value': rule[key]})
            # print(target_collect['rules'])

=======
        img_init = mongo.db.images.find_one({'_id': ObjectId(img['imageId'])})
        if img_init is None:
            return {'msg': 'No such image!',
                    'errorLog': None
                    }, 404
        # if not len(img['labels']) == 0:
        #     img_dict = {'imageID': index, 'type': img['labels'][0], 'object': img_init['interpretation']['object'],
        #                 'overlap': img_init['interpretation']['overlap']}
        #     lst.append(img_dict)
        #     index += 1
        #### Only for testing
        if index == 1:
            img_dict = {'imageID': index, 'type': 'non-life', 'object': img_init['interpretation']['object'],
                        'overlap': img_init['interpretation']['overlap']}
        else:
            img_dict = {'imageID': index, 'type': 'life', 'object': img_init['interpretation']['object'],
                        'overlap': img_init['interpretation']['overlap']}
        lst.append(img_dict)
        index += 1
    try:
        print(lst)
        print("FOIL input success")

        a = FOIL(lst)
        print("FOIL success")
        print(a)
        rule = FOIL(lst)[0]
        natural_rule = FOIL(lst)[1]
        print(rule)
        print(natural_rule)
    except Exception as err:
        return {'msg': 'ERROR in FOIL',
                'errorLog': str(err)
                }, 500
    # Loop over add into clauses
    for key in rule:
        flag = 0
        for rules in target_collect['rules']:
            if key == rules['label']:
                # rules['value'] = rule[key]
                rules['value'].clear()
                # for val in rule[key]:
                #     for clause in val:
                #         new_cl = {'value': clause}
                #         rules['value'].append(new_cl)
                i = 0
                j = 0
                while i < len(rule[key]):
                    while j < len(rule[key][i]):
                        new_cl = {'value': rule[key][i][j],
                                  'naturalValue': natural_rule[key][i][j]}
                        rules['value'].append(new_cl)
                        j += 1
                    i += 1
                flag = 1
        if flag == 0:
            new_rule = {'label': key, 'value': []}
            # for val in rule[key]:
            #     for clause in val:
            #         new_cl = {'value': clause}
            #         new_rule['value'].append(new_cl)
            i = 0
            j = 0
            while i < len(rule[key]):
                while j < len(rule[key][i]):
                    new_cl = {'value': rule[key][i][j],
                              'naturalValue': natural_rule[key][i][j]}
                    new_rule['value'].append(new_cl)
                    j += 1
                i += 1

            target_collect['rules'].append(new_rule)
    print("This is target_collection[rules]")
    print(target_collect['rules'])
>>>>>>> a51f06438e78a2a4cbcc4591308bf3c542b379ce
    target_collect_lst = wrksp['collections']
    i = 0
    flag = 0
    while i < len(target_collect_lst):
        if target_collect_lst[i]['_id'] == target_collect['_id']:
            target_collect_lst[i] = target_collect
            flag = 1
        i += 1
    print("This is target collection list")
    print(target_collect_lst)
    if flag == 0:
        return {'code': 2,
                'msg': 'No such collection!',
                'errorLog': None
                }

    flt = {'_id': ObjectId(body['workspaceID'])}
    new_wrksp = {'$set': {'collections': target_collect_lst}}

    # Need to be changed to update_one
    try:
        mongo.db.Workspace.update_one(flt, new_wrksp)
    except Exception as err:
<<<<<<< HEAD
        return {'code': 2,
                'msg': 'Fail to Update!',
                'errorLog': err
                }
=======
        return {'msg': 'Fail to Update!',
                'errorLog': str(err)
                }, 404
>>>>>>> a51f06438e78a2a4cbcc4591308bf3c542b379ce

    return {'code': 0, 'msg': "success", 'errorLog': None}

# @app.route('/flaskadmin')
# def mainpage():
#     return render_template("index.html")
