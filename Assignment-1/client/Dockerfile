
FROM python:latest

ADD client.py /client/

WORKDIR /client/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "client.py"]
