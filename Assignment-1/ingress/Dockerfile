# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 1
FROM python:latest

ADD ingress/ingress.py /ingress/
COPY commonResources/ /ingress/

WORKDIR /ingress/

EXPOSE 49668/udp

ENTRYPOINT ["python3", "-u", "ingress.py"]
