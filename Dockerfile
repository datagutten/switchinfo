###########
# BUILDER #
###########

# pull official base image
FROM python:3.11 AS builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsnmp-dev
RUN pip install --upgrade pip poetry poetry-plugin-export

COPY switchinfo switchinfo
COPY pyproject.toml switchinfo/pyproject.toml

RUN poetry -C switchinfo export -f requirements.txt --output requirements.txt --without-hashes --with postgres --with backup --with aoscx --with snmp
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r switchinfo/requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels gunicorn

#########
# FINAL #
#########

FROM python:3.11

# create the appropriate directories
ENV APP_HOME=/home/switch_info
ENV SNMP_LIBRARY=ezsnmp

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsnmp-dev git

# copy project
COPY switch_info $APP_HOME
COPY switchinfo $APP_HOME/switchinfo
COPY launcher.sh $APP_HOME

# Set up git repository for config backup
RUN mkdir /home/config_backup
RUN git --git-dir /home/config_backup/.git init
RUN git --git-dir /home/config_backup/.git config user.email "config@backup.local"
RUN git --git-dir /home/config_backup/.git config user.name "Config backup"

EXPOSE 8000

# Collect static and start gunicorn
RUN python /home/switch_info/manage.py collectstatic

RUN chmod +x launcher.sh
CMD ["./launcher.sh"]
