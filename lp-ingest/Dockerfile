FROM python:3
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait
CMD /wait && npm start

COPY src/ .
RUN chmod +x /submit.sh
CMD ["/bin/bash", "/submit.sh"]