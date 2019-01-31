
# Targetted-seq-qc-iu

User interface for browsing QC data from targetted seq experiment

## Getting Started

Before running the app there are you have to perform some setup.

First clone the repo by running `git clone`.

### Prerequisites

In order to run this application you have to have `python3` installed together with `python3-pip`.

### Installing

In order to run this app you have to install `requirements.txt` file by running:
```
pip3 install -r requirements.txt
```

### Running

When everything is installed you have to change directory to `targetted-seq-qc-ui`. Then just run `python3 app.py`.

### Dockerfile

If you want to use docker there is a Dockerfile provided.

To build the image it you have to run:
```
docker build --tag ngs .
```

Starting container:
```
docker run --name targetted-web-ui -p 80:80 -d ngs
```

## Authors

* **Dawid Sielski** - *Initial work*  [Dawid Sielski](https://github.com/dawidsielski)

## License

TODO

## Acknowledgments

Special thanks to my supervisor Pawel Sztromwasser.