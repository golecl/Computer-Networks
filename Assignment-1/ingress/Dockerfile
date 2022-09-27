FROM python:latest

# VOLUME /commonResources/

ADD ingress.py /ingress/

# COPY commonFunctions.py ./commonResources/

WORKDIR /ingress/

# THIS IS ESSENTIAL FOR THE CLIENT SERVER COMMUNICATION
EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "ingress.py"]
