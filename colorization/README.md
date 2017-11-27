colorization
================

This function applies color to a black and white image. It uses the [Caffe project](https://github.com/BVLC/caffe) and a pre-trained model. 

## Caffe:

> Caffe is a deep learning framework made with expression, speed, and modularity in mind. It is
> developed by Berkeley AI Research (BAIR)/The Berkeley Vision and Learning Center (BVLC) and
> community contributors.

## Operating modes:

There are two operating modes - the first uses minio for storing images and is used by this
repository by default. The binary mode is best for testing / bench-marking.

### Mode 1: minio

Mode one takes a JSON input and provides an output, see the source-code for the format.

Before calling the function make the image available within the minio bucket "colorization" using
`mc cp` or the minio SDK.


### Mode 2: binary

The binary mode does not require the use of a minio bucket to store input or output images. Just
deploy the function without specifying minio configuration. Call the function by passing in the
binary source image and capture the result to a local file.



