FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends virtualbox python3 python3-pip python3-setuptools wget unzip bash git && \
    wget https://releases.hashicorp.com/packer/1.3.1/packer_1.3.1_linux_amd64.zip && unzip packer_1.3.1_linux_amd64.zip -d packer && \
    mv packer/packer /usr/local/bin/ && chmod a+x /usr/local/bin/packer && rm packer_1.3.1_linux_amd64.zip && rmdir packer

CMD ["/bin/bash"]
