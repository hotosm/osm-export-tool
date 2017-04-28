FROM debian

ENV DEBIAN_FRONTEND noninteractive

RUN \
  apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    openssh-client \
    python-pip \
    python-yaml \
    software-properties-common \
  && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
  && add-apt-repository -y \
   "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
  && apt-get update \
  && apt-get install -y --no-install-recommends docker-ce \
  && pip install docker-compose
