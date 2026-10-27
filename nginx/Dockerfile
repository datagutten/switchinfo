FROM ghcr.io/datagutten/switchinfo:latest AS static
RUN python /home/switch_info/manage.py collectstatic --noinput

FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

COPY --from=static /home/switch_info/static /app/static