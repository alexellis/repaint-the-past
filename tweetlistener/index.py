import os, json, time, tempfile, sys, io, urllib, requests, contextlib
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from minio import Minio
from minio.error import ResponseError

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = io.BytesIO()
    yield
    sys.stdout = save_stdout

auth = OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
auth.set_access_token(os.environ['access_token'], os.environ['access_token_secret'])

minioClient = Minio(os.environ['minio_hostname'],
                  access_key=os.environ['minio_access_key'],
                  secret_key=os.environ['minio_secret_key'],
                  secure=False)

class TweetListener(StreamListener):
    def on_data(self, data):
        try:
            tweet = json.loads(data)
            print('Got tweet from %s "%s" (%i followers)' % (tweet['user']['screen_name'], tweet['text'], tweet['user']['followers_count']))
            if not tweet['retweeted']:
                if (tweet['extended_entities'] and tweet['extended_entities']['media']):
                    print('Got %i media items' % len(tweet['extended_entities']['media']))
                    for media in tweet['extended_entities']['media']:
                        if (media['type'] == 'photo'):
                            print("Ooooo a photo")
                            image_data = urllib.urlopen(media['media_url_https']).read()

                            now = str(int(round(time.time() * 1000)))
                            filename_in = now + '.jpg'
                            filename_out = now + '_output.jpg'
                            file_path_in = tempfile.gettempdir() + '/' + filename_in

                            with open(file_path_in, 'wb') as f:
                                f.write(image_data)

                            with nostdout():
                                minioClient.fput_object('colorization', filename_in, file_path_in)

                            headers = {'X-Callback-Url': 'http://gateway:8080/async-function/tweetpic'}
                            json_data = {
                                "image": filename_in,
                                "output_filename": filename_out,
                                "status_id": tweet['id_str']
                            }
                            r = requests.post('http://gateway:8080/async-function/colorization', json=json_data, headers=headers)
                            if (r.status_code == requests.codes.accepted):
                                print("Colorization succeeded for -> " + media['media_url_https'])
                            else:
                                print("Colorization failed for -> " + media['media_url_https'])
                        else:
                            print("Not a photo :(")
                else:
                    print('No media :(')
            else:
                print("Oh... a retweet")
        except Exception as e:
            print("error oops", e)

    def on_error(self, status):
        print('Error from tweet streamer', status)

if __name__ == '__main__':
    print('Setting up')
    l = TweetListener()
    stream = Stream(auth, l)

    print('Listening for tweets')
    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['@colorisebot'])
