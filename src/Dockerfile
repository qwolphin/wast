FROM python:3.11

# create sudo user mimicking host user
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

ARG HOST_USER
ARG HOST_UID
RUN useradd -m --uid ${HOST_UID?} ${HOST_USER?} && \
    usermod -aG sudo ${HOST_USER?} && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache -r /requirements.txt

USER $HOST_USER
