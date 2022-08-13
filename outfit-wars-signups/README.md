# Outfit Wars Signup Checker

This script uses the [Lithafalcon API](https://census.lithafalcon.cc) and census to retrieve info about Outfit Wars signups.

By default it retrieves all servers' outfit signups. This can be filtered to a single server with the --server-name option.

## Getting started

This tool uses python's built in module venv to create a virutal environment so it doesn't mess with your system's local packages.

Create venv:

```shell
python -m venv .venv
```

Activate venv:

```shell
. .venv/bin/activate
```

Install dependencies:

```shell
pip install -r requirements.txt
```

## Using the tool
```
usage: main.py [-h] [--server-name {Emerald,Connery,Soltech,Miller,Cobalt}]
               [--outfit-id]
               service_id

positional arguments:
  service_id            Your service id for accessing Census

options:
  -h, --help            show this help message and exit
  --server-name {Emerald,Connery,Soltech,Miller,Cobalt}, -s {Emerald,Connery,Soltech,Miller,Cobalt}
  --outfit-id, -o       Output outfit ids in addition to tags
```