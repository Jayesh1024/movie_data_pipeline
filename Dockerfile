FROM apache/airflow:latest-python3.9
USER root
RUN apt-get update && apt-get install -y vim && apt-get install -y wget

RUN wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome.deb && \
    rm google-chrome.deb

RUN mkdir /opt/src
WORKDIR /opt/src

COPY . .

RUN chown -R airflow .
USER airflow

RUN pip install -r requirements.txt


