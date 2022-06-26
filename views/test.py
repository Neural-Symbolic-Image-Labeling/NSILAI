from app import app
from flask import jsonify, request

@app.route('/test', methods=['GET'])
def test():
    return jsonify("Hello World!")

@app.route('/test/objdetec', methods=['POST'])
def objdetec():
    data = request.get_json()
    return jsonify(data["name"])
