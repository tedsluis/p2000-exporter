FROM python:slim-bullseye

WORKDIR /python-container

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY exporter.py .

ENTRYPOINT [ "python3", "/python-container/exporter.py" ]
#CMD [ "python3", "/python-container/exporter.py" ]
