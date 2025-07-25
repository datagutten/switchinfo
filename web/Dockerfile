FROM debian:latest AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip wget ca-certificates
RUN wget -O /home/gitlist.zip "https://github.com/klaussilveira/gitlist/releases/download/2.0.0/gitlist-2.0.0.zip"

WORKDIR /home/gitlist
RUN unzip /home/gitlist.zip

FROM php:8.1-apache

RUN apt-get update && \
    apt-get install -y --no-install-recommends git

COPY --from=builder /home/gitlist /var/www/html

COPY ./apache.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod rewrite
RUN a2enmod proxy
RUN a2enmod proxy_http

COPY launcher.sh /home/launcher.sh
RUN chmod +x /home/launcher.sh
COPY --from=datagutten/switchinfo:latest /home/switch_info/static /var/www/html/static

# Expose the port Apache listens on
EXPOSE 80

# Start Apache when the container runs
CMD ["/home/launcher.sh"]