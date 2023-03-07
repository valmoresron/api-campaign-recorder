# Introduction

A python app that can record and download campaigns into videos.

# How to run using Python

- Note - This has only been tested on a linux machine.
- Make sure your system has the following requirements:
  - Python 3.10 and up
  - Pipenv
  - Google Chrome
  - xvfb
  - ffmpeg
- Navigate the terminal to this folder
- Run `pipenv shell` all proceeding commands must be done inside this shell
- Run `pipenv install`
- Run `python run.py` or `./run.sh`

# How to run using Docker

- Note - Running this in Docker will not auto-reload the app when you have changes
- Make sure you have docker installed on your system
- Run `./docker-build.sh` to build the image
- Run `./docker-run.sh` to run the image

# How to run using Docker Compose

- Run `docker-compose up`
- Run `docker-compose down` to stop

# Notes

Framerate might be choppy if you have a slow hardware
