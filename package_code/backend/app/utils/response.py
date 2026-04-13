from flask import jsonify


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "message": message, "data": data})


def error(message, code=1):
    return jsonify({"code": code, "message": message, "data": None}), 400
