FROM ubuntu:latest
MAINTAINER mohamed2811 "mohamed.2811@icloud.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y libmysqlclient-dev
COPY . /app1
WORKDIR /app1
ENV PYTHONPATH /app1
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]