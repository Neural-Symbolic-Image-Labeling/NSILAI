from app import app
from flask import jsonify

@app.route('/test', methods=['GET'])
def test():
    return jsonify("Hello World!")