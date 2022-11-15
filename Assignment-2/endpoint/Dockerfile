# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

FROM python:latest

ADD endpoint/endpoint.py /endpoint/
COPY common.py/ /endpoint/

WORKDIR /endpoint/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "endpoint.py"]