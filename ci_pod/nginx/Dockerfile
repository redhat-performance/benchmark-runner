FROM ubuntu:20.04

ARG USER
ARG TOKEN
ENV TOKEN=$TOKEN
ENV USER=$USER

RUN apt-get update && apt-get install -y nginx openssl apache2-utils && \
    htpasswd -b -c /etc/nginx/.htpasswd "$USER" "$TOKEN"
# generate randon certificate
# RUN openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj "/C=US/ST=A/L=B/O=C/CN=D" -keyout /mykey.key  -out /mycrt.crt

# IBM cloud dns credentials
COPY ibm_private.key /ibm_private.key
COPY ibm_crt.crt /ibm_crt.crt
COPY ibm_conf.conf /etc/nginx/sites-available/default
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["nginx", "-g", "daemon off;"]
