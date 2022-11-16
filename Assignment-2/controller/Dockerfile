# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

FROM python:latest

ADD controller/controller.py /controller/
COPY common.py/ /controller/

WORKDIR /controller/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "controller.py"]