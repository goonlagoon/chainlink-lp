FROM python:3
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait
CMD /wait && npm start

ENV PYTHONHASHSEED 1

COPY submit.sh /
RUN chmod +x /submit.sh

COPY requirements.txt /app/
RUN cd /app \
      && pip3 install -r requirements.txt

COPY . /app
RUN chmod +x /app/src/ingest.py

CMD ["/bin/bash", "/submit.sh"]