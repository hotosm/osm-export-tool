FROM ubuntu:16.04
WORKDIR /usr/local/src

RUN \
  apt update \
  && apt upgrade -y \
  && apt install -y build-essential git libsqlite3-dev qt5-default

RUN \
  git clone --recursive --depth 1 https://github.com/mapsme/omim.git

WORKDIR /usr/local/src/omim

RUN \
  echo | ./configure.sh \
  && CONFIG="gtool no-tests" tools/unix/build_omim.sh -cr
