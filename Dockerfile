FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3 gnupg

WORKDIR /opt/install_apm

ADD . .
