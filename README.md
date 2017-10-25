# repaint-the-past

![](https://github.com/alexellis/repaint-the-past/raw/master/colorisation-architecture.png)

# Deployment

## Minio

You'll need a [Minio](https://minio.io) server running to store the images in.


* Run Minio once and capture the secret/access keys and inject into the command above.

```
$ docker run -ti --rm minio/minio server /data
...
AccessKey: ZBPIIAOCJRY9QLUVEHQO
SecretKey: vMIoCaBu9sSg4ODrSkbD9CGXtq0TTpq6kq7psLuE
...
```

Hit Control+C and set up two environmental variables:

```
export MINIO_ACCESS_KEY="ZBPIIAOCJRY9QLUVEHQO"
export MINIO_SECRET_KEY="vMIoCaBu9sSg4ODrSkbD9CGXtq0TTpq6kq7psLuE"
```

We found running a single-container minio server was the easiest way as I had issues when running the distributed version. Once Minio is deployed, go and create a new bucket called `colorization`. This is where the images will be stored.

```
$ docker run -dp 9000:9000 \
  --restart always --name minio \
  -e "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  -e "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  minio/minio server /data
```

> You can optionally add a bind-mount too by adding the option: `-v /mnt/data:/data -v /mnt/config:/root/.minio`

## OpenFaaS functions

Firstly, you'll need to make sure the OpenFaaS gateway is configured to have larger read & write timeouts as the colorise function can sometimes take a few seconds to return.

```
$ docker service update func_gateway \
  --env-add "write_timeout=60" \
  --env-add "read_timeout=60"
```

Create `credentials.yml` with these contents:

```yaml
environment:
  minio_secret_key: <minio secret key>
  minio_access_key: <minio access key>
  minio_url: <minio url>
```

Do not include HTTP in the `minio_url`.

For example:

```
environment:
  minio_secret_key: vMIoCaBu9sSg4ODrSkbD9CGXtq0TTpq6kq7psLuE
  minio_access_key: ZBPIIAOCJRY9QLUVEHQO
  minio_url: 192.168.0.10:9000
```

And now deploy the OpenFaaS functions

```
$ faas-cli deploy -f stack.yml
```

# Invocation

## Configure Minio (object storage)

* Download the CLI

Download the Minio client from: https://github.com/minio/mc

* Add the Docker container running Minio as a host

```
$ export IP=192.168.0.1   # replace with the Docker host IP
$ mc config host add minios3 http://$IP:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
```

* Create a bucket

```
$ mc mb minios3/colorization
Bucket created successfully minios3/colorization.
```

* Upload an image to your minio bucket:

```
$ curl -sL https://static.pexels.com/photos/276374/pexels-photo-276374.jpeg > test_image_bw.jpg && \
  http_proxy="" mc cp test_image_bw.jpg minios3/colorization
```

* Then call the function:

```
$ http_proxy="" curl -d '{"image": "test_image_bw.jpg"}' \
  http://127.0.0.1:8080/function/colorization

{"duration": 8.719741106033325, "image": "1508788935770_output.jpg"}
```

The returned image is the path to the converted image in minio.

So copy it back to your host:

```
$ mc cp minios3/colorization/1508788935770_output.jpg .
$ open 1508788935770_output.jpg
```

Congratulations - you just recoloured the past! Read on for how we hooked this into a Twitter bot.

# Twitter extension

If you want to replicate our DockerCon demo which listens for tweets matching a certain criteria & then replies with the colourised image, follow the instructions below.

You need to deploy the `tweetlistener` service. This will listen for tweets matching a certain criteria and then forward the requests into the `colorise` function. Make sure you only deploy one replica of `tweetlistener` because otherwise you'll get duplicate events.

Create `tweetlistener.envs` with the following contents:

```
# tweetlistener.envs (add your values below)
minio_access_key=<minio access key>
minio_secret_key=<minio secret key>
minio_hostname=<minio url>
consumer_key=<twitter consumer key>
consumer_secret=<twitter consumer secret>
access_token=<twitter token>
access_token_secret=<twitter token secret>
```

```
$ docker service create --name tweetlistener \
  --env-file tweetlistener.envs \
  --network func_functions \
  developius/tweetlistener:latest
```

Update `credentials.yml` to add your Twitter details

```yaml
environment:
  minio_secret_key: <minio secret key>
  minio_access_key: <minio access key>
  minio_url: <minio url>
  consumer_key: <twitter consumer key>
  consumer_secret: <twitter consumer secret>
  access_token: <twitter token>
  access_token_secret: <twitter token secret>
```

Then re-deploy

```
$ faas-cli deploy -f twitter_stack.yml
```

# Tweet it
You can now tweet [@colorisebot](https://twitter.com/colorisebot) (or your own twitter account) with your image and see the data flow through the functions. Depending on the underlying infrastructure, it should take about 10s for the whole flow from tweeting the image, to receiving the tweeted reply.

# Colourising video

We've shown how we can colourise photos, but our original goal was to colourise video.
There are a couple of scripts we've written to do this.

## Prerequisite

You need to install some dependencies before you can run the code.

```
$ pip install -r requirements.txt
```

## Splitting frames

First, modify line 2 of `split_frames.py` to use the path to your video file.

Now you can run the script which splits up all the frames & outputs them into `frames/` (make sure this folder exists).

```
$ python split_frames.py
```

## Colourising the frames

Next you need to run the actual colourisation code. To do this, you must first start up the docker container which will run the colourisation.

```
$ docker run -a STDERR -e write_timeout=60 -e read_timeout=60 -p 8080:8080 --rm developius/openfaas-colorization:0.1
```

Now you can run `colourise_frames.py` to generate the colourised frames.

```
$ python colourise_frames.py
```

This will create all the colourised frames in the folder `output/` (make sure this one exists too).

## Stitch them back together

The final step is to stitch them back together with `ffmpeg`.
ffmpeg can be installed via brew with `brew install ffmpeg` and is available on most other platforms too.

```
$ ffmpeg -framerate 24 -i output/%05d.jpg output.mp4
```

Now check your current directory for a file name `output.mp4`. Whoop, you just colourised the past, again!
