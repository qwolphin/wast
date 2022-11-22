FROM python:3.11 as requirements

# create sudo user mimicking host user
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

ARG HOST_UID
RUN useradd -m --uid ${HOST_UID?} user && \
    usermod -aG sudo user && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN mkdir -m 777 /docs

COPY requirements.txt /requirements.txt
RUN sudo pip3 install --no-cache -r /requirements.txt

USER $HOST_USER
ENV PYTHONPATH=/app

FROM requirements as complete

COPY --chown=user README.md /README.md
COPY --chown=user src/ /app 
