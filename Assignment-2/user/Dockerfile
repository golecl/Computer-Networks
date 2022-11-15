# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

FROM python:latest

ADD user/user.py /user/
COPY common.py/ /user/

WORKDIR /user/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "user.py"]