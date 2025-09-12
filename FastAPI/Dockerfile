FROM python:3.13-alpine AS build

RUN apk add build-base libpq-dev
COPY ./requirements-build.txt .
RUN pip install --no-cache-dir -r requirements-build.txt

FROM python:3.13-alpine AS final

RUN apk add --no-cache libpq

WORKDIR home/app

COPY . .
RUN pip install --no-cache-dir -r requirements-final.txt
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages


CMD ["uvicorn" , "main:app", "--host", "0.0.0.0"]