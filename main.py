import os
from support import helpers as common
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

mongo = common.get_secrets('MONGO')
config = common.get_document_by_id("gcr-pos", mongo, "common", "configs")
Response = Response
jsonify = jsonify
secret = common.get_secrets('HEADER')


@app.route("/orders", methods=['post', 'get'])
def handle_hdnl_orders_inbound():
    from backend_services import capture_requests as cr
    return cr.read_endpoint(request)


if __name__ == "__main__":
    app.run(debug=config.debug, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
