from flask import jsonify, request
import base64


# import json
#
# with open('data.json', 'r') as json_file:
#     data = json.load(json_file)
#
# # print(data)
#
# s = {k: data[0][k] for k in ['object', 'overlap'] if k in data[0]}
# # print(data[0][1:3])
# print(s)
# #
# print(len(s))
# @app.route('/test', methods=['GET'])
# def test():
#     return jsonify("Hello World!")
#
# @app.route('/test/objdetec', methods=['POST'])
# def objdetec():
#     data = request.get_json()
#     return jsonify(data["name"])

#
# base64_img = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAA' \
#             'LEwEAmpwYAAAB1klEQVQ4jY2TTUhUURTHf+fy/HrjhNEX2KRGiyIXg8xgSURuokX' \
#             'LxFW0qDTaSQupkHirthK0qF0WQQQR0UCbwCQyw8KCiDbShEYLJQdmpsk3895p4aS' \
#             'v92ass7pcfv/zP+fcc4U6kXKe2pTY3tjSUHjtnFgB0VqchC/SY8/293S23f+6VEj' \
#             '9KKwCoPDNIJdmr598GOZNJKNWTic7tqb27WwNuuwGvVWrAit84fsmMzE1P1+1TiK' \
#             'MVKvYUjdBvzPZXCwXzyhyWNBgVYkgrIow09VJMznpyebWE+Tdn9cEroBSc1JVPS+' \
#             '6moh5Xyjj65vEgBxafGzWetTh+rr1eE/c/TMYg8hlAOvI6JP4KmwLgJ4qD0TIbli' \
#             'TB+sunjkbeLekKsZ6Zc8V027aBRoBRHVoduDiSypmGFG7CrcBEyDHA0ZNfNphC0D' \
#             '6amYa6ANw3YbWD4Pn3oIc+EdL36V3od0A+MaMAXmA8x2Zyn+IQeQeBDfRcUw3B+2' \
#             'PxwZ/EdtTDpCPQLMh9TKx0k3pXipEVlknsf5KoNzGyOe1sz8nvYtTQT6yyvTjIax' \
#             'smHGB9pFx4n3jIEfDePQvCIrnn0J4B/gA5J4XcRfu4JZuRAw3C51OtOjM3l2bMb8' \
#             'Br5eXCsT/w/EAAAAASUVORK5CYII='
#
# base64_img_bytes = base64_img.encode('utf-8')
# decoded_image_data = base64.b64decode(base64_img_bytes)
# print(decoded_image_data)
# print("".join(["{:08b}".format(x) for x in decoded_image_data]))

# if target_rule is []:
#     rule = {
#         'label': '', # label need to be added
#         'value': rule,
#     }, {'_id': 'false'}
#     target_rule.append(rule)
# else:
#     new_rule = {'$set': {'value': rule}}
#     target_rule.append(new_rule)

#################### Testing for foil api ##################

# body = {
#     'workspacename': '123',
#     'collectionname': '123'
# }
# wrk = {
#     'name': '123',
#     'collections': [{
#         'name': '123',
#         'rules': []
#     },
#         {
#             'name': '456',
#              'rules': [1, 2, 3]
#         }]
#
# }
#
# mongo.db.Workspace.insert_one(wrk)
# wrksp = mongo.db.Workspace.find_one({'name': body['workspacename']})
# target_collect = None
# for collect in wrksp['collections']:
#     # print(collect['name'])
#     # print(body['collectionname'])
#     if collect['name'] == body['collectionname']:
#         target_collect = collect
# if target_collect is None:
#     return 'No such image collection!'

#################### Testing for pretrain api ##################

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

########################### Used Code in FOIL flask
# if not target_collect['rules']:
#     # target_collect['rules'].append({'label': key, 'value': rule[key]})
#     # Modification for new rule schema
#     # target_collect['rules']['label'] = key
#     # for val in rule[key]:
#     #     for clause in val:
#     #         new_cl = {'value': clause}
#     #         target_collect['rules']['value'].append(new_cl)
#     new_rule = {'label': key, 'value': []}
#     for val in rule[key]:
#         for clause in val:
#             new_cl = {'value': clause}
#             new_rule['value'].append(new_cl)
#     target_collect['rules'].append(new_rule)
#
# else:

#
#
# def send_rule():
#     return {'rule1': [[1, 2, 3], [1, 2, 3]], 'rule2': [[1, 2, 3], [1, 2, 3]]}


# @app.route('/flaskadmin/pretrain', methods=['GET'])
# @app.route('/api/img/pre/<imgid>', methods=['POST'])
# def pretrain(imgid):
#     # image_id = request.args.get('_id')
#     # base64_img_bytes = image_id.encode('utf-8')
#     target = mongo.db.image.find_one({'_id': imgid})
#     if target is None:
#         return {'msg': 'No such image, id is invalid!',
#                 'errorLog': None
#                 }, 404
#     base64_img_bytes = target['data']
#     base64_img = base64_img_bytes[base64_img_bytes.rfind(','):]
#
#     decoded_image_data = base64.b64decode(base64_img)
#     # bin_im = "".join(["{:08b}".format(x) for x in decoded_image_data])
#
#     # Run pretrained model
#     # json_res = pretrain_label(decoded_image_data)
#
#     # Saving the output json to specific image
#     # data = json.load(json_res)
#
#     # For testing
#     try:
#         data = pretrain_label(decoded_image_data, imgid)
#     except Exception as err:
#         return {'msg': 'ERROR in pre-train',
#                 'errorLog': err
#                 }, 500
#
#     # data = json.load(data)
#     interpretation = {k: data[0][k] for k in ['object', 'overlap'] if k in data[0]}
#     # print(interpretation)
#     new_int = {'$set': {'interpretation': interpretation}}
#     try:
#         mongo.db.image.update_one(target, new_int)
#     except Exception as err:
#         return {'msg': 'Fail to Update!',
#                 'errorLog': err
#                 }, 400
#
#     return {'code': 0, 'msg': "success", 'errorLog': None}, 200
