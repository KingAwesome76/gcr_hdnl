import os

from flask import Flask, Response, request, jsonify

app = Flask(__name__)

Response = Response
jsonify = jsonify


@app.route("/orders", methods=['post', 'get'])
def handle_hdnl_orders_inbound():
    from backend_services import capture_requests as cr
    return cr.read_endpoint(request)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
