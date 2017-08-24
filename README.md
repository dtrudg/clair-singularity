# clair-singularity

<a href="https://codeclimate.com/github/dctrud/clair-singularity"><img src="https://codeclimate.com/github/dctrud/clair-singularity/badges/gpa.svg" /></a>
<a href="https://travis-ci.org/dctrud/clair-singularity"><img src="https://travis-ci.org/dctrud/clair-singularity.svg?branch=master"></a>
[![Coverage Status](https://coveralls.io/repos/github/dctrud/clair-singularity/badge.svg?branch=master)](https://coveralls.io/github/dctrud/clair-singularity?branch=master)

__Scan [Singularity](http://singularity.lbl.gov/) container images for security vulnerabilities
using [CoreOS Clair](https://github.com/coreos/clai).__

The [CoreOS Clair vulnerability scanner](https://github.com/coreos/clair) is a useful tool able to scan docker and other container
formats for security vulnerabilities. It obtains up-to-date lists of vulerabilities for various
platforms (namespaces) from public databases.

We can use Clair to scan singularity containers, by exploiting the fact that an exported .tar.gz of a
singularity container image is similar to a single layer docker image.

This tool:

   * Exports a singularity image to a temporary .tar.gz file (this will be under $TMPDIR)
   * Computes the SHA256 hash as a unique name to pass to Clair
   * Serves the .tar.gz file via an in-built http server, so the Clair service can retrieve it
   * Calls the Clair API to ingest the .tar.gz file as a layer for analysis
   * Calls the Clair API to retireve a vulnerability report for this layer
   * Displays a simple text, or full JSON format report

Based on experiments detailed [in this Gist](https://gist.github.com/dctrud/479797e5f48cfe39cdb4b50a15e4c567)


__IMPORTANT NOTES__

This tool is currently a quick hack, not heavily tested. Use at your own risk. 

There is no support yet for SSL client certificates to verify that we are sending API requests to a trusted
Clair instance, or that only a trusted Clair instance can retrieve images from the inbuilt http server.
*This means that this solution is insecure except with an isolated local install of Clair*.
 

## Requirements

To use clair-singularity you will need a _Linux_ host with:

  * Python 2.7 or greater installed
  * Singularity installed (tested with 2.3.1) and the singularity executable in your `PATH`
  * A Clair instance running somewhere, that is able to access the machine you will run 
  clair-singularity on. It's easiest to accomplish this using docker to run a local Clair instance as below.
  
  
## Starting a local Clair instance

If you have docker available on your local machine, the easiest way to start scanning your
Singularity images is to fire up a Clair instance locally, with docker. The official Clair docker images
are a blank slate, and do not include any vulnerability information. At startup Clair will have to
download vulnerability information from the internet, which can be quite slow. Images from github
user arminc are available that include pre-seeded databases:

https://github.com/arminc/clair-local-scan

To startup a Clair instance locally using these instances:

```bash
docker run -d --name db arminc/clair-db:20187-08-21
docker run -p 6060:6060 --link db:postgres -d --name clair arminc/clair-local-scan:v2.0.0
```

*Replace the clair-db:2017-08-21 image tag with a later date for newer vulnerabilities*


## Installation

Clone the git repo, or download and extract the zip then:

```bash
python setup.py install
```


## Usage

__Clair on same machine__

To scan a singularity image, using a clair instance running at the localhost, on port 6060 (as above):

    clair-singularity myimage.img
    
To scan a singularity image, using a clair instance at a different URI on the localhost (e.g. behind
a reverse proxy):

    clair-singularity --clair-uri http://127.0.0.1:80/clair myimage.img

__Clair on a different machine__

By default, clair-singularity uses a python simple http server binding on localhost port 8088 to make
the .tar.gz available to the Clair server for scanning. If you are running clair-singularity on a
different machine than clair you must instruct the http server to listen to a public interface, that
the Clair server is able to talk to, e.g:

    clair-singularity --clair-uri http://10.0.1.202:6060 --bind-ip=10.0.1.201 --bind-port=8088 myimage.img

__Full JSON Reports__

By default, clair-singularity gives a simplified text report on STDOUT. To obtain the full JSON
report returned by Clair use the `--jsoon-output` option.

    clair-singularity --json-output myimage.img


## Development / Testing

Tests are run using using pytest inside a docker container, via a script that will bring up a clair instance and run
clair-singularity within a correctly linked container:

    ./docker_local_tests.sh
