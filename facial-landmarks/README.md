# Facial Landmarks example with dlib, OpenCV in the Chrysalis Cloud

This example shows how you can build your own Facial Landmark detection in the cloud.

## Prerequsities

- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- [Install OBS Studio](https://obsproject.com/)


Clone the repository if you haven't done so already:
```
https://github.com/chryscloud/chryscloud-ai-examples.git
```

Download pre-trained shape predictor model in the 'data' folder:
```
cd facial-landmarks/data
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
```

Unzip the model: 
```
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

Create and activate conda environment:
```
cd ..
conda env create -f environment.yml
conda activate chrysface
```

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
python face_landmarks.py
```

If you don't have a chrysalis connection string create your developer account [here](https://cloud.chryscloud.com) and click on `Your first RTMP stream`.



