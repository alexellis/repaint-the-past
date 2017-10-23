# repaint-the-past

![](https://github.com/alexellis/repaint-the-past/raw/master/colorisation-architecture.png)

# Deployment

## Minio

You'll need a [Minio](https://minio.io) server running to store the images in.
I found running a single-container minio server was the easiest way as I had issues when running the distributed version.

```
$ docker run -dp 9000:9000 \
  --restart always --name minio -e \
  "MINIO_ACCESS_KEY=<key>" -e "MINIO_SECRET_KEY=<secret>" \
  -v /mnt/data:/data -v /mnt/config:/root/.minio \
  minio/minio server /data
```


## OpenFaaS functions

Create `credentials.yml` with these contents:

```yaml
environment:
  minio_secret_key: <minio secret key>
  minio_access_key: <minio access key>
  minio_url: <minio url>

```

And now deploy the OpenFaaS functions

```
$ faas-cli deploy -f stack.yml
```

# Invocation

Upload an image to your minio bucket & then simply call the function:

```
$ curl -d '{"image:"filename.jpg"}' http://127.0.0.1:8080/function/colorization
{"duration": 8.719741106033325, "image": "1508788935770_output.jpg"}
```

The returned image is the path to the converted image in minio.

# Twitter extension

If you want to replicate our DockerCon demo which listens for tweets matching a certain criteria & then replies with the colourised image, follow the instructions below.

You need to deploy the `tweetlistener` service. This will listen for tweets matching a certain criteria and then forward the requests into the `colorise` function. Make sure you only deploy one replica of `tweetlistener` because otherwise you'll get duplicate events.

Create `tweetlistener.envs` with the following contents:

```
# tweetlistener.envs (add your values below)
minio_access_key=<minio access key>
minio_secret_key=<minio secret key>
minio_hostname=<minio url>
```

```
$ docker service create --name tweetlistener \
  --env-file tweetlistener.envs
  --image developius/tweetlistener:latest
  --network func_functions
```

Now uncomment the lines in `stack.yml` for the `tweetpic` function & redeploy:

```
$ faas-cli deploy -f stack.yml
```

# Tweet it
You can now tweet [@colorisebot](https://twitter.com/colorisebot) (or your own twitter account) with your image and see the data flow through the functions. Depending on the underlying infrastructure, it should take about 10s for the whole flow from tweeting the image, to receiving the tweeted reply.
