# Covid19 Mask Detector

This example is an modification of an existing tutorial by [Adrian Rosebrock](https://www.pyimagesearch.com/author/adrian/) to work with Chrysalis Cloud. 

Please visit tutorial [COVID-19: Face Mask Detector with OpenCV, Keras/TensorFlow, and Deep Learning](https://www.pyimagesearch.com/2020/05/04/covid-19-face-mask-detector-with-opencv-keras-tensorflow-and-deep-learning/) site if you'd like to know how to prepare a dataset and train your own network. 

## Prerequsities

- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- [Install OBS Studio](https://obsproject.com/)

Clone the repository if you haven't done so already:
```
https://github.com/chryscloud/chryscloud-ai-examples.git
```

Create and activate conda environment:
```
cd ..
conda env create -f environment.yml
conda activate chryscovid
```

In this example we're using a pre-trained models from the above mentioned original tutorial.

If you need more information on [how to stream to Chrysalis cloud visit our page for instructions](https://chryscloud.com/documentation/how-to-stream-from-web-cam-to-chrysalis/)

## Run

Get Chrysalis Cloud SDK streaming credentials for your connected camera (OBS Studio in this case)
```
export chrys_port=1111
export chrys_host=url.at.chrysvideo.com
export chrys_password=mypassword
export chrys_cert=pathtomycertificate.cer
```

Run the example:
```python
python mask_detection.py
```

If you don't have a chrysalis connection string create your developer account [here](https://cloud.chryscloud.com) and click on `Your first RTMP stream`.
