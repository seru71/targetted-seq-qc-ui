FROM tiangolo/uwsgi-nginx-flask:python3.7

MAINTAINER Dawid Sielski "dawid.sielski@outlook.com"

VOLUME . /app

WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python", "index.py"]

