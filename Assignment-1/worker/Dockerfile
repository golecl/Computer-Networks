# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 1
FROM python:latest

ADD worker/worker.py /worker/
COPY commonResources/ /worker/
ADD worker/files /worker/

WORKDIR /worker/

EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "worker.py"]
