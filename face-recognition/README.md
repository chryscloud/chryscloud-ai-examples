# Face Recognition from multiple cameras

## Prerequsities:

- install anaconda
- install postgresql

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

