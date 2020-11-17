# Face Recognition from multiple cameras

## Prerequsities:

- [install anaconda](https://docs.anaconda.com/anaconda/install/)
- [install docker](https://docs.docker.com/engine/install/)
- [install docker-compose](https://docs.docker.com/compose/install/)
- [install postgresql](https://www.postgresql.org/download/)
- Have at least one CCTV Network Camera (RTSP protocol, H.264)

Prepare postgres user. Start by activating postgres prompt:
```
sudo -i -u postgres
```

Create new user and database:
```sql
createuser --interactive --pwprompt
createdb -O user db
```

Connect to postgres database and create a schema:
```sql
psql db
create extension if not exists cube;
drop table if exists faces;
create table faces (id serial, name varchar, vec_low cube, vec_high cube);
create index faces_idx on faces (vec_low, vec_high);
```

On Ubuntu 18.04 installing `libpq-dev` may be required:
```
sudo apt-get install libpq-dev
```

## Setup development environment

```
conda env create -f environment.yml
```

Initialize conda environment
```
conda activate chryfaceoff
```

Set environment variables for PostgreSQL connection in your terminal:
```
export db_name=db
export db_host=localhost
export db_user=yourusername
export db_password=mypassword
```

## Import celebrity faces (optional)

Open up a file `import_images.py` and find global variable `FACES_ROOT_DIR`. Change it to your preferred folder. 

You can find the celebrity face recognition dataset on the bottom of this readme file under `Celebrity Face Recognition Dataset`.

Run the import script:
```python
python import_images.py
```
## Import your face and family members into database

```
python server.py
```

You can validate if the image recognition is working and determine the recognition cutoff / threshold at certain euclidean distance.

Navigate with your browser to:
```
http://localhost:5001
```

To run recognition click on `Test recognition`. 

To add a "face" to the database first click `Take Photo`, the fill out `Name` and click `Upload photo`. 

To modify the threshold
Open `server.py` and find this code block:

```python
if best_result['distance'] > 0.5:
        resp = jsonify(success=True)
        return resp
```
You can see we have a distance of 0.5 as our threshold set up.

Modify treshold to your needs if necessary.

## Connecting multiple CCTV Cameras

Visit our [example GitHub repository for `Chrysalis Edge Proxy`](https://github.com/chryscloud/video-edge-ai-proxy) and copy-paste `docker-compose.yml` contents from the documentation into your own docker compose yml file. 

Make sure to create a folder under the chrysedgeserver portion from:
```yml
 volumes:
      - /data/chrysalis:/data/chrysalis
      - /var/run/docker.sock:/var/run/docker.sock
```
to 
```yml
 volumes:
      - /your/custom/folder:/data/chrysalis
      - /var/run/docker.sock:/var/run/docker.sock
```

Now open a terminal window and run:
```
docker-compose up --no-build
```

This will start the chrysalis edge proxy. Now navigate to `http://localhost:8905` and add your RTSP cameras. 

## Run ccvt_cams.py

`cctv_cams.py` runs under the same Anaconda environment as the rest of the code in this example. So make sure to activate it. It also uses the same PostgreSQL database connection as all other samples using environment variables.

Run the cctv_cams.py:
```
python cctv_cams.py 
```

If you'd like to see what's happening uncomment `display_cameras(queue, channel, cameras)` in the main method.

# Resources

- [Celebrity Face Recognition Dataset](https://github.com/prateekmehta59/Celebrity-Face-Recognition-Dataset)
- [PostgreSQL Cube](https://www.postgresql.org/docs/10/cube.html)
