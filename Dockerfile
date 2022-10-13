FROM apache/airflow:2.4.1
USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      libreoffice \
      openjdk-11-jdk

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow

COPY ./requirements.txt /opt/airflow/requirements.txt

RUN pip install -r /opt/airflow/requirements.txt