# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

FROM python:latest

ADD forwarder/forwarder.py /forwarder/

WORKDIR /forwarder/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "forwarder.py"]