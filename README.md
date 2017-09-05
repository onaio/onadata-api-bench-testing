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
