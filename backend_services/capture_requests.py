from datetime import datetime
import json
import flask
import xmltodict
from support import helpers as common
from backend_services import allowed


mongo = dict()
secret = dict()
config = dict()
BLOB_BASE = config.get('blob_base')
PROJECT = config.get('project')
ENV = config.get('env')
_LOGGER = common.initiate_logging(__name__)


def get_set_globals():
    global config, mongo, _LOGGER, BLOB_BASE, PROJECT, ENV
    if not mongo:
        mongo = common.get_secrets('MONGO')
    if not config:
        config = common.get_document_by_id("gcr_hdnl", mongo, "common", "configs")
        BLOB_BASE = config.get('blob_base')
        PROJECT = config.get('project')
        ENV = config.get('env')
    if not _LOGGER:
        _LOGGER = common.initiate_logging(__name__)
    return


def check_for_globals(func):
    get_set_globals()
    return func


def get_bucket(message_type):
    buckets = {
               "order": f"ijit_orders_{ENV}"
               }
    return buckets.get(message_type, f"ijit_unknown_{ENV}")


def get_topic(message_type):
    topics = {
              "order": f"{PROJECT}enterprise_orders_{ENV}"
              }
    return topics.get(message_type)


def read_endpoint(request):
    if flask.request.method == 'POST':
        if not allowed(request.headers, secret):
            _LOGGER.warning("no match for header credentials")
            return flask.Response(json.dumps({"error": "access denied"}), status=401, mimetype="application/json")
        if not request.data:
            response = {"validation_warning": "no body",
                        "status": "record not captured"}
            _LOGGER.warning(f'schema_check: {response}')
            return flask.Response(json.dumps(response), status=200, mimetype="application/json")
        get_set_globals()
        doc_hash = hash(request.data)
        _LOGGER.info(request.get_data())
        extension = common.ext(request.content_type)
        if extension == 'xml':
            message_content = xmltodict.parse(request.get_data())
        else:
            message_content = json.loads(request.get_data())
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S%f")
        type_ = message_content.get('type', 'no_type')
        blob_prefix = f'{BLOB_BASE}/{type_}/'
        file_name = f'{blob_prefix}msg_{ts}_{doc_hash}.{extension}'
        common.store_to_bucket(request.data, file_name, request.content_type, buck=get_bucket(type_))
        if get_bucket(type_) == f"ijit_unknown_{ENV}":
            no_type_response = {"info": "a 'no_type' message has been stored. Only typed messages will be accepted.",
                                "rec_locator": hash(file_name)
                                }
            return flask.Response(json.dumps(no_type_response), status=201, mimetype="application/json")

        common.publish(message_content, get_topic(type_), msg_type=type_, source='pos')
        common.publish(message_content, f"{PROJECT}pos_feed", msg_type=type_, source='pos')
        this_collection = f"axi_inbound_{type_}"
        common.write_data_to_collection(message_content, mongo, 'pos', this_collection)
        response = dict(rec_locator=hash(file_name), type=type_, status='captured')
        return flask.Response(json.dumps(response), status=202, mimetype="application/json")
    if flask.request.method == 'GET':
        response = {"status": "active"}
        print(f'health_check: {response}')
        return flask.Response(json.dumps(response), status=200, mimetype="application/json")
    else:
        return flask.Response(status=400)
