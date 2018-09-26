FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends virtualbox python3 python3-pip python3-setuptools wget unzip bash git && \
    wget https://releases.hashicorp.com/packer/1.2.5/packer_1.2.5_linux_amd64.zip && unzip packer_1.2.5_linux_amd64.zip -d packer && \
    mv packer/packer /usr/local/bin/ && chmod a+x /usr/local/bin/packer && rm packer_1.2.5_linux_amd64.zip && rmdir packer

# Config between delimiters taken from https://github.com/jenkinsci/docker/blob/master/Dockerfile
# --
ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1006
# [...]
ARG JENKINS_HOME=/var/jenkins_home

ENV JENKINS_HOME $JENKINS_HOME

# Jenkins is run with user `jenkins`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid
RUN groupadd -g ${gid} ${group} \
  && useradd -d "$JENKINS_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user}

USER ${user}
# --

CMD ["/bin/bash"]
