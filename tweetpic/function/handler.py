import twitter, os, json, time, tempfile, contextlib, sys, io

from PIL import Image
from minio import Minio
from minio.error import ResponseError

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = io.BytesIO()
    yield
    sys.stdout = save_stdout

minioClient = Minio(os.environ['minio_url'],
                  access_key=os.environ['minio_access_key'],
                  secret_key=os.environ['minio_secret_key'],
                  secure=False)

api = twitter.Api(
    consumer_key=os.environ['consumer_key'],
    consumer_secret=os.environ['consumer_secret'],
    access_token_key=os.environ['access_token'],
    access_token_secret=os.environ['access_token_secret']
)

"""
Input:
{
  "status_id": "twitter status ID",
  "image": "minio_path_to_image.jpg"
}
"""

def handle(req):
    filename = tempfile.gettempdir() + '/' + str(int(round(time.time() * 1000))) + '.jpg'
    in_reply_to_status_id = req['status_id']
    duration = req['duration']

    with nostdout():
        minioClient.fget_object('colorization', req['image'], filename)

    with open(filename, 'rb') as image:
        size = os.fstat(image.fileno()).st_size
        im = Image.open(filename)
        if size > 5 * 1048576:
            maxsize = (1028, 1028)
            im.thumbnail(maxsize, Image.ANTIALIAS)
        im = im.convert("RGB")
        im.save(filename, "JPEG")
        image = open(filename, 'rb')

        status = api.PostUpdate("I colorized your image using #openfaas in %.1f seconds #dockercon" % duration,
            media=image,
            auto_populate_reply_metadata=True,
            in_reply_to_status_id=in_reply_to_status_id)
        image.close()
        return {
            "reply_to": in_reply_to_status_id,
            "status_id": status.id
        }
