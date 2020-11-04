# Finger Counting with OpenCV

This example shows one of the possible ways to count number of fingers (hand gesture) from a real-time remote video stream. 

## Prerequisites

- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- [Install OBS Studio](https://obsproject.com/) or check [other ways to stream to chrysalis cloud](https://chryscloud.com/documentation/how-to-stream-from-web-cam-to-chrysalis/).


Clone the repository if you haven't done so already:
```
https://github.com/chryscloud/chryscloud-ai-examples.git
```

Navigate to `finger-counting` folder:
```
cd finger-counting
```

Create and activate conda environment:
```
conda env create -f finger-environment.yml
conda activate chrysfingercount
```

## Run

Get Chrysalis Cloud SDK streaming credentials for your connected camera:
```
export chrys_port=1111
export chrys_host=url.at.chrysvideo.com
export chrys_password=mypassword
export chrys_cert=pathtomycertificate.cer
```

Run the example:
```python
python fingercounting.py
```

