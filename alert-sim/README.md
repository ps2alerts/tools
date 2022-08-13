# Alert Simulator

This tool is used to generate an alert and stuff it full of dummy data, rather than having to wait for the game to provide it to you and running the whole collection system to start working.

It also enables testing of continents we cannot access, e.g. for Outfitwars.

## Getting started

This tool uses pipenv to grab local dependencies. It creates a virutal environment so it doesn't mess with your systems local packages.

Install pipenv:

```shell
pip3 install pipenv
```

Install dependencies:

```shell
pipenv install
```

Run the tool
```shell
./run.sh
```

You may need to run `pipenv shell` and execute `pip3 install certifi` within it, I had trouble with that despite it being "installed".

[More info on pipenv](https://pipenv.pypa.io/en/latest/install/#installing-packages-for-your-project)
