
FROM python:latest

RUN pip install func-timeout
ADD client/client.py /client/
COPY commonResources/ /client/

WORKDIR /client/

VOLUME ./endFiles:/endFiles

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "client.py"]
