from flask import Flask, jsonify, request

from date_webhook.utils.payload import Payload
from date_webhook.fulfillment import fulfill

import json

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle():
    json_request = request.json
    req = Payload(json_request)
    print(req.payload)
    fulfill(req)
    return jsonify(req.get())
