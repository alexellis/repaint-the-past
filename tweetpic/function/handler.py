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

def requeue(st):
    # grab from headers or set defaults.
    retries = int(os.getenv("Http_X_Retries", "0"))
    max_retries = int(os.getenv("Http_X_Max_Retries", "9999")) # retry up to 9999
    delay_duration = int(os.getenv("Http_X_Delay_Duration", "60")) # delay 60s by default

    # Bump retries up one, since we're on a zero-based index.
    retries = retries + 1

    headers = {
        "X-Retries": str(retries),
        "X-Max-Retries": str(max_retries),
        "X-Delay-Duration": str(delay_duration)
    }

    r = requests.post("http://mailbox:8080/deadletter/tweetpic", data=json.dumps(st), json=False, headers=headers)

    print "Posting to Mailbox: ", r.status_code
    if r.status_code!= 202:
        print "Mailbox says: ", r.text

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

        try:
            status = api.PostUpdate("I colourised your image in %.1f seconds. Find out how: https://subr.pw/s/cmpb5x7" % duration,
                media=image,
                auto_populate_reply_metadata=True,
                in_reply_to_status_id=in_reply_to_status_id)

            return {
                "reply_to": in_reply_to_status_id,
                "status_id": status.id
            }

        except twitter.error.TwitterError, e:
            for m in e.message:
                if m['code'] == 34 or m['code'] == 385:
                    print('Tweet %i went missing' % in_reply_to_status_id)
                    break
                if m['code'] == 88:
                    print('We hit the API limits, queuing %i' % in_reply_to_status_id)
                    requeue(req)
                    break

        image.close()
        return {
            "reply_to": in_reply_to_status_id,
            "status_id": False
        }
