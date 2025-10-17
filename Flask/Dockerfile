# To keep docker image as small as can it need to build from python alpine version. But on alpine couldn't
# install psycopg2 automatically which needs for running flask app in a container. Need to install build-base
# and libpq-dev (postgresql interact) packages on linux layer. 
# To make even smaller can make multi stage docker build and just copy installed build packages to final
# articles:
#    https://wbarillon.medium.com/docker-python-image-with-psycopg2-installed-c10afa228016
#    https://stackoverflow.com/questions/42424108/installing-psycopg2-in-an-alpine-docker-container 

FROM python:3.10-alpine AS build

RUN apk add build-base libpq-dev

COPY ./app/requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

FROM python:3.10-alpine AS final

RUN apk update \
    && apk upgrade \
    && apk add --no-cache libpq

WORKDIR Flask/

COPY ./app .
COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages


CMD ["python" , "minihome.py"]