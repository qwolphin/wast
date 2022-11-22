FROM python:3.11 as requirements

# create sudo user mimicking host user
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

ARG HOST_USER
ARG HOST_UID
RUN useradd -m --uid ${HOST_UID?} ${HOST_USER?} && \
    usermod -aG sudo ${HOST_USER?} && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN mkdir -m 777 /docs

COPY src/requirements.txt /requirements.txt
RUN sudo pip3 install --no-cache -r /requirements.txt

USER $HOST_USER
ENV PYTHONPATH=/app

FROM requirements as complete

COPY README.md /README.md
COPY src/ /app 
