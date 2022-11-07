# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 1

FROM python:latest

ADD client/client.py /client/
COPY commonResources/ /client/

WORKDIR /client/

VOLUME ./endFiles:/endFiles

EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "client.py"]
