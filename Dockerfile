FROM python:3-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /cdpnotify

COPY . /cdpnotify

RUN pip install -r requirements.txt
RUN pip install -e .

RUN apk del .build-deps

ENTRYPOINT ["cdpnotify"]