FROM python:latest

ADD ingress/ingress.py /ingress/
COPY commonResources/ /ingress/

WORKDIR /ingress/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "ingress.py"]
