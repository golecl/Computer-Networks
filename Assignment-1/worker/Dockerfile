
FROM python:latest

RUN pip install func-timeout
ADD worker/worker.py /worker/
COPY commonResources/ /worker/
ADD worker/files /worker/

WORKDIR /worker/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "worker.py"]
