FROM python:3.7

ENV WORKDIR=/opt
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
ENV PYTHONUNBUFFERED 1


WORKDIR $WORKDIR
