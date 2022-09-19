FROM python:latest

ADD ingress.py /ingress/

WORKDIR /ingress/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "ingress.py"]
