# Dockerfile for Yandex Transport Monitor Tests
# Architectures: armhf (Orange PI, Raspberry PI)
#                x86-64

# Use Ubuntu 18.04 as basis
FROM ubuntu:18.04

# ----- CHANGE THESE ARGUMENTS TO YOUR DESIRES ----- #
# -- ИЗМЕНИТЕ ДАННЫЕ АРГУМЕНТЫ ДЛЯ ВАШЕЙ СИТУАЦИИ -- #
# TimeZone / Часовой Пояс
ARG timezone=Europe/Moscow

# -------------------------------------------------- #

# Setting frontend to non-interactive, no questions asked, ESPECIALLY for locales.
ENV DEBIAN_FRONTEND=noninteractive

# Install all required software, right way.
# We're using all latest package versions here. Risky.
RUN apt-get update && \
    apt-get install -y \
    locales \
    tzdata \
    python3 \
    python3-pip

# Install pytest
RUN pip3 install pytest \
                 pytest-progress \
                 pytest-rerunfailures \
                 pytest-timeout


# Dealing with goddamn locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Setting the goddamn TimeZone
ENV TZ=${timezone}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cleaning
RUN apt-get clean

# Creating the user
RUN mkdir -p /home/transport_api
RUN mkdir -p /home/transport_api/testdata/output
RUN useradd transport_api --home /home/transport_api --shell /bin/bash

# Copying project
ADD yandex_transport_webdriver_api/* /home/transport_api/yandex_transport_webdriver_api/

# Copying tests
ADD tests/* /home/transport_api/tests/
ADD tests/testdata/* /home/transport_api/testdata/
ADD execute_tests.sh /home/transport_api
ADD continuous_tests.sh /home/transport_api
ADD function_monitoring.sh /home/transport_api

RUN chown -R transport_api:transport_api /home/transport_api
WORKDIR /home/transport_api

USER transport_api:transport_api
CMD /home/transport_api/execute_tests.sh
