FROM python:3-alpine

WORKDIR /cdpnotify

COPY . /cdpnotify

RUN pip install -r requirements.txt
RUN pip install -e .

ENTRYPOINT ["cdpnotify"]