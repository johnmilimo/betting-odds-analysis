ARG PYTHON_VERSION=3.7.0
FROM python:${PYTHON_VERSION}

RUN mkdir -p /usr/src/app && apt-get update

COPY requirements.txt /tmp/
ONBUILD COPY . /usr/src/app
WORKDIR /usr/src/app

RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["/bin/bash", "./run.sh"]