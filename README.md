# Load testing Ona API with Locust

## Setup

```
$ mkvirtualenv locust
$ pip install pip-tools
$ pip-sync
```

## Usage

Create a csv file named 'users.csv' with username and password of the users you
want to use as clients in a test. See an example below:

```
"bob","bob bob"
"alice","alice"
```

Start the locust server.

```
$ locust -f zebra_user.py --host=https://stage-api.ona.io
```

Go to localhost:8089 and start a swarm.


## Monitoring with StatsD and Graphite

Use the following steps to setup local instances of StatsD and Graphite:

```
cd ..
git clone https://github.com/hopsoft/docker-graphite-statsd.git
cd docker-graphite-statsd
docker build -t hopsoft/graphite-statsd .
docker run -d --name graphite --restart=always -p 80:80 -p 2003-2004:2003-2004 -p 2023-2024:2023-2024 -p 8125:8125/udp -p 8126:8126 hopsoft/graphite-statsd
```

You can then graph the stats you want to monitor using Grafana. [grafana.json](./grafana.json) is a sample Grafana dashboard you can import into your Grafana setup. You will need to create datasources to point to Graphite, CloudWatch (for monitoring the database).