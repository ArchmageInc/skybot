FROM python:3.9-alpine
EXPOSE 8888

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-deps gcc musl-dev

COPY ./src ./

#docker run -d -v sky_gifs:/usr/src/gifs --name=skybot archmageinc/skybot
CMD [ "python", "-u", "skybot.py" ]