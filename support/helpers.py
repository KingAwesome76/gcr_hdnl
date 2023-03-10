from ijr import firefly
from functools import wraps
import json
from base64 import b64decode
from os import environ
from google.cloud import secretmanager_v1 as sm
from ijr.gcp_lib import PubSubPublisher
from ijr.mongo_lib import MongoWriter, MongoReader
import uuid
import google.cloud.logging as gcp_logging
import logging
import datetime
from google.cloud import storage

MongoWriter.find = MongoReader.find

_LOGGER = None


def check_for_logger(funct):
    global _LOGGER
    if not _LOGGER:
        _LOGGER = initiate_logging(__name__)
    return funct


def default_object(o):
    """ Default handler for json.dumps()"""
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    raise TypeError("Type %s not serializable" % type(o))


def get_uuid(change):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, json.dumps(change, default=str)))


def initiate_logging(log_name):
    this_logger = logging.getLogger(log_name)
    cloud_logging_client = gcp_logging.Client()
    cloud_logging_client.setup_logging()
    return this_logger


def cleaner(string_value):
    if not string_value:
        return string_value
    if "'" in string_value:
        result = string_value.replace("'", "''")
        return result
    return string_value


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def response_dot():
    response_message = {"invalid_type": "type changes are ignored by this worker",
                        "success": "mastering successful",
                        "invalid_source": "source is not for EDS_curator",
                        "missing_attributes": "Curation requires an MD Delta message with attributes"
                        }
    return firefly.NestedNamespace(response_message)


def listener(message):
    def listen_to(func):
        @wraps(func)
        def event(_event, context):
            _context = context
            attributes = _event["attributes"]
            print('attributes', attributes)
            if message in attributes:
                data = json.loads(b64decode(_event['data']).decode('utf-8'))
                return func(data, attributes)
            else:
                print('No job for me. Going to sleep!')
                return

        return event

    return listen_to


def get_secrets(secret_target):
    if isinstance(secret_target, str):
        target = environ.get(secret_target)
        try:
            return json.loads(target)
        except json.JSONDecodeError:
            scraped_id = environ.get('GCP_PROJECT')
            if scraped_id:
                client = sm.SecretManagerServiceClient()
                name = f"projects/{scraped_id}/secrets/{target}/versions/latest"
                secret = client.access_secret_version(name=name)
                _payload = secret.payload.data.decode('UTF-8')
                payload = json.loads(_payload)
                return payload
            return


def store_to_bucket(doc, file_name, content, buck=None):
    client = storage.Client()
    bucket = client.bucket(buck)
    blob = bucket.blob(file_name)
    future = blob.upload_from_string(doc, content_type=content)
    return future


def store(this_doc, credentials, collection, this_doc_key):
    db_name, col_name = collection.split(".")
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as this_consumer:
        written = this_consumer.write_data(doc=this_doc, doc_key=this_doc_key)
        return written


def remove_null_fields(this_dict: dict):
    clean = {key: value for key, value in this_dict.items() if value}
    return clean


def publish(publish_message, topic, msg_type, source):
    if topic is None:
        return
    with PubSubPublisher(topic=topic,
                         msg_type=msg_type,
                         source=source) as publisher:
        published = publisher.publish(publish_message)

    return published


def get_document_by_id(identifier, credentials, db_name, col_name):
    query = {"_id": identifier}
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as read:
        target = read.find(read.db_name, read.col_name, query)
        return next(target, {})


def get_document_by_query(query, credentials, db_name, col_name, filter=None) -> dict:
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as read:
        target = read.find(read.db_name, read.col_name, query, projection=filter)
        return next(target, {})


def get_documents_by_query(query, credentials, db_name, col_name, filter=None) -> list:
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as read:
        target = read.find(read.db_name, read.col_name, query, projection=filter)
        return list(target)


def edit_by_query(query, update, credentials, db_name, col_name, many=None):
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as editor:
        amount = "many" if many else "one"
        future = editor.edit_data(query, update, amount)
        return future


def write_data_to_collection(data, credentials, db_name, col_name):
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as writer:
        if isinstance(data, list):
            futures = list()
            for each_document in data:
                if not each_document:
                    continue
                this_future = writer.write_data(each_document, each_document.get('_id', get_uuid(each_document)))
                futures.append(this_future)
            return futures
        future = writer.write_data(data, data.get('_id', get_uuid(data)))
        return future


def delete_docs(query, credentials, db_name, col_name):
    with MongoWriter(mdb_server=credentials['MDB_SERVER'], mdb_pass=credentials['MDB_PASS'],
                     mdb_user=credentials['MDB_USER'],
                     db_name=db_name, col_name=col_name) as writer:

        this_db = writer._client['db_name']
        this_col = this_db['col_name']
        deleted = this_col.delete_many(query)

    return f"{deleted.deleted_count} documents"


def clean_up_list(data):
    new_data = []
    for v in data:
        if isinstance(v, dict):
            v = cleanup_dict(v)
        elif isinstance(v, list):
            v = clean_up_list(v)
        if v not in (None, str(), list(), dict()):
            new_data.append(v)
    return new_data


def cleanup_dict(data):
    new_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            v = cleanup_dict(v)
        elif isinstance(v, list):
            v = clean_up_list(v)
        if v not in (None, str(), list(), dict()):
            new_data[k] = v
    return new_data


