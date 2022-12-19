1. install psql, create a database called "financial_data", use the .sql file to restore

2. install docker, make sure that you can run docker command without sudo

3. add a file called "config.py" under dir "compute/data/database/", format is like
```
psql_config = {
    "database": 'financial_data',
    "user": '',
    "password": '',
    "host": 'psql-server ip on local'
}
```
It should be able to connect to the psql db on local from container

3. backend_api serve static files at path backend_api/public/,
assume the url is 127.0.0.1:3000

4. if the backend_api url is 127.0.0.1:3000, then the 7th line of
frontend/src/App.js should be `const base_url = '127.0.0.1:3000'`,
and the page is available on 127.0.0.1:3001

* start / restart the service : sh start.sh
* daily update : cd compute && sh routine.sh
