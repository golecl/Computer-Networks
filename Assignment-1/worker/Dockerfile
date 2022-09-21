
FROM python:latest

ADD worker.py /worker/
ADD test1.txt /worker/
ADD test2.txt /worker/
ADD test3.txt /worker/
ADD test4.txt /worker/

WORKDIR /worker/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "worker.py"]
