FROM python:3.10.4-slim-buster

WORKDIR /home

# install system requirements
RUN apt-get update
RUN apt-get install -y wget xvfb ffmpeg libxss1 libappindicator1 libindicator7

# install google chrome
# you can check official versions here: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
ARG CHROME_VERSION="103.0.5060.134-1"
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get install -y /tmp/chrome.deb


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./recordings /code/recordings

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]