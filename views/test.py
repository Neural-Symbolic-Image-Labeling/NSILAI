from app import app
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
