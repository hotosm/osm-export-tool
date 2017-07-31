FROM nginx

RUN \
  apt update \
  && apt install -y --no-install-recommends \
    ca-certificates \
    curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && curl -L https://github.com/lukas2511/dehydrated/archive/master.tar.gz | \
  tar zxf - --strip-components=1 -C /usr/local/bin \
  && mkdir -p /usr/share/nginx/html/.well-known

# overwrite Nginx's default config
COPY ops/exports.conf /etc/nginx/conf.d/default.conf

# copy a dehydrated config for Let's Encrypt
COPY ops/dehydrated.config /etc/dehydrated/config
