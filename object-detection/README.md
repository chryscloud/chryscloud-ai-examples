# Object detection in live video stream with Chrysalis Cloud

##  Using a pre-trained model to detect objects in an image

This example is modified from the Object detection example in [TensorFlow Model Garden repository](https://github.com/tensorflow/models). It shows how an existing AI/ML model can be easily adapted to run on Chrysalis Cloud and real-time video streams. 

The original notebook that runs on invididual images can be found [here](https://github.com/tensorflow/models/blob/master/research/object_detection/colab_tutorials/object_detection_tutorial.ipynb)

## Using Chrysalis cloud to detect objects in real-time video stream

This example is assuming you have a GPU capable graphics card. By default it assumes: 
- `cudatoolkit=10.1`
- `cudnn=7.6.5`

Modify `environment.yml` to fit your installed drivers. 

If you'd like to run it on CPU please chech the `environment.yml` file and make appropriate modifications before creating a new conda environment (e.g. change  `tensorflow-gpu==2.1.0` to `tensorflow==2.1.0`).

Check GPU card information:
```
nvidia-smi
```

Check cuda version:
```
nvcc --version
```
or 
```
cat /usr/local/cuda/version.txt
```

Check cudnn version:
```
cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2
or
cat /usr/include/cudnn.h | grep CUDNN_MAJOR -A 2
```

## Prerequsities

- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- [Install OBS Studio](https://obsproject.com/)

Clone the repository if you haven't done so already:
```
https://github.com/chryscloud/chryscloud-ai-examples.git
```

Create and activate conda environment:
```
conda env create -f environment.yml
conda activate chrysobject
```

If you need more information on [how to stream to Chrysalis cloud visit our page for instructions](https://chryscloud.com/documentation/how-to-stream-from-web-cam-to-chrysalis/)

## Tensorflow model setup

After creating and activating conda environment clone the tensorflow models:

```
cd object-detection
git clone --depth 1 https://github.com/tensorflow/models
```

Compile the protos:
```
cd models/research
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .
python -m pip install .
cd ../..
cp -r models/research/object_detection object_detection
```

In case you have trouble with OpenCV try this on Ubuntu or Debian try this within `chrysobject` environment:
```
conda remove opencv
conda install --channel menpo opencv
```

## Run

Get Chrysalis Cloud SDK streaming credentials for your connected camera (OBS Studio in this case)
```
export chrys_port=1111
export chrys_host=url.at.chrysvideo.com
export chrys_password=mypassword
export chrys_cert=pathtomycertificate.cer
```

Run the object detection example:
```
python object_detection.py
```

If you don't have a chrysalis connection string create your developer account [here](https://cloud.chryscloud.com) and click on `Your first RTMP stream`.





