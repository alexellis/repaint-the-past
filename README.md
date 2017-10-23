# repainting-the-past

![](https://github.com/alexellis/repaint-the-past/raw/master/colorisation-architecture.png)

# Deployment

You'll need a [Minio](https://minio.io) server running to store the images in.
I found running a single-container minio server was the easiest way as I had issues when running the distributed version.

```
$ docker run -dp 9000:9000 --restart always --name minio -e "MINIO_ACCESS_KEY=<key>" -e "MINIO_SECRET_KEY=<secret>" -v /mnt/data:/data -v /mnt/config:/root/.minio minio/minio server /data
```

Next you need to deploy the `tweetlistener` service. This will listen for tweets matching a certain criteria and then forward the requests into the `colorise` function. Make sure you only deploy one replica of `tweetlistener` because otherwise you'll get duplicate events.

Create `env.list` with the following contents:

```
# env.list (add your values below)
consumer_key=<twitter consumer key>
consumer_secret=<twitter consumer secret>
access_token=<twitter access token>
access_token_secret=<twitter access secret>
minio_access_key=<minio access key>
minio_secret_key=<minio secret key>
minio_hostname=<minio url>
```

```
$ docker service create --name tweetlistener --env-file env.list
```

# Invocation
You can now tweet [@colorisebot](https://twitter.com/colorisebot) (or your own twitter account) with your image and see the data flow through the functions. Depending on the underlying infrastructure, it should take about 10s for the whole flow from tweeting the image, to receiving the tweeted reply.
