FROM alpine:3.10

ENV SPARK_VERSION=3.0.0
ENV HADOOP_VERSION=3.2

COPY crontab.txt /
COPY entry.sh /
COPY submit.sh /

RUN apk add --no-cache curl bash java-postgresql-jdbc openjdk8-jre python3 py-pip nss libc6-compat coreutils procps \
      && ln -s /lib64/ld-linux-x86-64.so.2 /lib/ld-linux-x86-64.so.2 \
      && chmod +x *.sh \
      && wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
      && tar -xvzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
      && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark \
      && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
      && cd /

ENV PYTHONHASHSEED 1

RUN chmod +x /submit.sh /entry.sh
# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt /app/
RUN cd /app \
      && pip3 install -r requirements.txt

# Copy the source code
COPY . /app

RUN /usr/bin/crontab /crontab.txt

CMD ["/bin/bash", "/entry.sh"]