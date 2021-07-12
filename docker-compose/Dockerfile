FROM python:3.7.8-slim-buster

RUN set -ex \
    \
    && savedAptMark="$(apt-mark showmanual)" \
    && apt-get update \
    && apt-get install -y --no-install-recommends git \
	    dpkg-dev \
		gcc \
		libssl-dev \
		make

RUN python3 -m pip install --upgrade pip

RUN cd /usr/local/src/
WORKDIR /usr/local/src/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src/ .

EXPOSE 8080

CMD ["/usr/local/src/run.sh"]