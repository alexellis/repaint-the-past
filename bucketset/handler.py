from minio import Minio
from minio.error import ResponseError
import json
import os

# Request
# {
#   "inbox": "aellis_catjump_inbox",
#   "outbox": "aellis_catjump_outbox"
# }
def handle(st):
    req = json.loads(st)
    mc = Minio(os.environ['minio_authority'],
                    access_key=os.environ['minio_access_key'],
                    secret_key=os.environ['minio_secret_key'],
                    secure=False)
    try:
        res = mc.make_bucket(req["inbox"] , location='us-east-1')
    except ResponseError as err:
        print(err)
    try:
        res = mc.make_bucket(req["outbox"] , location='us-east-1')
    except ResponseError as err:
        print(err)

# Response
# Empty - success
# Non-empty - failure
