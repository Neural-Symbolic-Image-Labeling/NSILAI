from bson import ObjectId
from flask import *
from flask_cors import CORS
from flask_pymongo import PyMongo
import base64
from views.pretrain import pretrain_label
from views.foil import FOIL
from views.label import label

import os

app = Flask(__name__)
# CORS
cors = CORS(app)
# configuration
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nsil pog')

app.config.update(
    MONGO_HOST='localhost',
    MONGO_PORT=27017,
    MONGO_URI='mongodb://localhost:27017/NSIL'
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
@app.route('/api/img/pre/<imgid>', methods=['POST'])
def pretrain(imgid):
    # image_id = request.args.get('_id')
    # base64_img_bytes = image_id.encode('utf-8')
    target = mongo.db.images.find_one({'_id': ObjectId(imgid)})
    if target is None:
        return {'msg': 'No such image, id is invalid!',
                'errorLog': None
                }, 404
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
        data = pretrain_label(decoded_image_data, imgid)
    except Exception as err:
        return {'msg': 'ERROR in pre-train',
                'errorLog': str(err)
                }, 500

    # data = json.load(data)
    interpretation = {k: data[0][k] for k in ['object_detect', 'panoptic_segmentation'] if k in data[0]}
    # interpretation = {k: data[0][k] for k in ['object', 'overlap'] if k in data[0]}

    # print(interpretation)
    new_int = {'$set': {'interpretation': interpretation}}
    # new_int = {'$set': {'interpretation': {'object_detect': interpretation, 'panoptic_segmentation': {}}}}
    try:
        mongo.db.images.update_one(target, new_int)
    except Exception as err:
        return {'msg': 'Fail to Update!',
                'errorLog': str(err)
                }, 400

    return {'code': 0, 'msg': "success", 'errorLog': None}, 200


# @app.route('/flaskadmin/selectset', methods=['GET'])
# def select_set():
#     return render_template('selectset.html')


# Classification
@app.route('/api/autolabel', methods=['POST'])
def train_rule():
    body = request.get_json()
    wrksp = mongo.db.workspaces.find_one({'_id': ObjectId(body['workspaceID'])})
    if wrksp is None:
        return {'msg': 'No such workspace!',
                'errorLog': None
                }, 404
    target_collect = None

    for collect in wrksp['collections']:
        if collect['_id'] == ObjectId(body['collectionID']):
            target_collect = collect
    if target_collect is None:
        return {'msg': 'No such image collection!',
                'errorLog': None
                }, 404

    image_metas = target_collect['images']
    if image_metas is []:
        return {'msg': 'No images in the collection!',
                'errorLog': None
                }, 404
    lst = []
    index = 1
    # Add condition for no label
    for img in image_metas:
        img_init = mongo.db.images.find_one({'_id': ObjectId(img['imageId'])})
        if img_init is None:
            return {'msg': 'No such image!',
                    'errorLog': None
                    }, 404
        # if not len(img['labels']) == 0:
        #     img_dict = {'imageId': index, 'type': img['labels'][0], 'object_detect': img_init['interpretation']['object_detect'],
        #                 'panoptic_segmentation': img_init['interpretation']['panoptic_segmentation']}
        #     lst.append(img_dict)
        #     index += 1
        #### Only for testing
        if index == 1:
            img_dict = {'imageId': index, 'type': 'non-life',
                        'object_detect': img_init['interpretation']['object_detect'],
                        'panoptic_segmentation': img_init['interpretation']['panoptic_segmentation']}
        else:
            img_dict = {'imageId': index, 'type': 'life', 'object_detect': img_init['interpretation']['object_detect'],
                        'panoptic_segmentation': img_init['interpretation']['panoptic_segmentation']}
        lst.append(img_dict)
        index += 1
    try:
        print(lst)
        print("FOIL input success")
        result = FOIL(lst)
        rule = result[0]
        natural_rule = result[1]
        print(rule)
        print(natural_rule)
        print("FOIL success")
    except Exception as err:
        return {'msg': 'ERROR in FOIL',
                'errorLog': str(err)
                }, 500

    # Loop over add into clauses and overwrite rules
    target_collect['rules'].clear()
    for key in rule:
        new_rule = {'name': key,
                    'clauses': []}
        #### Modified version for more predicate in single clauses
        i = 0
        while i < len(rule[key]):
            new_cl = {'literals': []}
            j = 0
            while j < len(rule[key][i]):
                new_lit = {'literal': rule[key][i][j],
                           'naturalValue': natural_rule[key][i][j]}
                new_cl['literals'].append(new_lit)
                j += 1
            new_rule['clauses'].append(new_cl)
            i += 1
        target_collect['rules'].append(new_rule)

    print("This is target_collection[rules]")
    print(target_collect['rules'])

    # Labeling Task
    ##################
    label_lst = []
    img_id_lst = []
    index = 0
    # Image input
    for img in image_metas:
        img_init = mongo.db.images.find_one({'_id': ObjectId(img['imageId'])})
        if img_init is None:
            return {'msg': 'No such image!',
                    'errorLog': None
                    }, 404
        if (not img["labeled"]) or (img["labeled"] and not img["manual"]):
            img_dict = {'imageId': index, 'object_detect': img_init['interpretation']['object_detect'],
                        'panoptic_segmentation': img_init['interpretation']['panoptic_segmentation']}
            label_lst.append(img_dict)
            img_id_lst.append(index)
        index += 1
        #### Only for testing
        # if index == 1:
        #     img_dict = {'imageId': index, 'type': 'non-life', 'object': img_init['interpretation']['object'],
        #                 'overlap': img_init['interpretation']['overlap']}
        # else:
        #     img_dict = {'imageId': index, 'type': 'life', 'object': img_init['interpretation']['object'],
        #                 'overlap': img_init['interpretation']['overlap']}
        # lst.append(img_dict)
        # index += 1

    # Rule input
    rules = target_collect['rules']
    if rules is []:
        return {'msg': 'No rules in the collection!',
                'errorLog': None
                }, 404
    rule_dict = {}
    for rule in rules:
        rule_dict[rule['name']] = []
        for clause in rule['clauses']:
            cla_lst = []
            for lit in clause['literals']:
                cla_lst.append(lit['literal'])
            rule_dict[rule['name']].append(cla_lst)

    try:
        print(label_lst)
        print(rule_dict)
        print("label input success")

        labels = label(label_lst, rule_dict)

    except Exception as err:
        return {'msg': 'ERROR in Apply Rules (labeling)',
                'errorLog': str(err)
                }, 500

    if len(img_id_lst) != len(labels):
        return {'msg': 'Label method return insufficient labels based on input images',
                'errorLog': None
                }, 500

    # Apply new labels in
    # i = 0
    # while i < len(labels):
    #     if labels[i] != "None":
            # if not target_collect['images'][img_id_lst[i]]['labels']:
            #     label_dict = {
            #         'name': labels[i],
            #         'mark': {}
            #     }
            #     target_collect['images'][img_id_lst[i]]['labels'].append(label_dict)
            # else:
            #     # Implement later for other tasks
            #     target_collect['images'][img_id_lst[i]]['labels'][0]['name'] = labels[i]

            # target_collect['images'][img_id_lst[i]]['labeled'] = True
        # Later will apply coordinates
        # i += 1
    # Compatible with conflict labels
    i = 0
    while i < len(labels[0]):
        lst = []
        if [labels[0][i]] != 'None':
            lst = [labels[0][i]]
        for lab_lst in labels:
            if lab_lst[i] not in lst and lab_lst != 'None':
                lst.append(lab_lst[i])

        if not target_collect['images'][img_id_lst[i]]['labels']:
            label_dict = {
                'name': lst,
                'mark': {}
            }
            target_collect['images'][img_id_lst[i]]['labels'].append(label_dict)
        else:
            # Implement later for other tasks
            target_collect['images'][img_id_lst[i]]['labels'][0]['name'] = lst

        if not lst:
            target_collect['images'][img_id_lst[i]]['labeled'] = True
        i += 1

    print("Lable Success!")
    # Update statistics
    # Reset sta
    target_collect['statistics']['unlabeled'] = 0
    target_collect['statistics']['manual'] = 0
    target_collect['statistics']['autoLabeled'] = 0
    for img in image_metas:
        if img['labeled']:
            if img['manual']:
                target_collect['statistics']['manual'] += 1
            else:
                target_collect['statistics']['autoLabeled'] += 1
        else:
            target_collect['statistics']['unlabeled'] += 1

    # Updating workspace
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
        return {'msg': 'No such collection!',
                'errorLog': None
                }, 404

    flt = {'_id': ObjectId(body['workspaceID'])}
    new_wrksp = {'$set': {'collections': target_collect_lst}}

    try:
        mongo.db.workspaces.update_one(flt, new_wrksp)
    except Exception as err:
        return {'msg': 'Fail to Update!',
                'errorLog': str(err)
                }, 404

    return {'msg': "success", 'errorLog': None}, 200

#
# @app.route('/flaskadmin')
# def mainpage():
#     return render_template("index.html")
