FROM python:3.10.4-slim-buster

WORKDIR /home

# install system requirements
RUN apt-get update
RUN apt-get install -y wget xvfb ffmpeg libxss1 libappindicator1 libindicator7
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y -f ./google-chrome*.deb


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./recordings /code/recordings

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]