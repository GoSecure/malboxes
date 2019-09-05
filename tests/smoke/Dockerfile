FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    curl -sSL https://www.virtualbox.org/download/oracle_vbox_2016.asc | apt-key add - && \
    echo "deb http://download.virtualbox.org/virtualbox/debian xenial contrib" >> /etc/apt/sources.list.d/virtualbox.list && \
    apt-get update && apt-get install -y --no-install-recommends virtualbox-5.2 module-init-tools python3 python3-pip python3-setuptools wget unzip bash git && \
    wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip && unzip packer_1.4.3_linux_amd64.zip -d packer && \
    mv packer/packer /usr/local/bin/ && chmod a+x /usr/local/bin/packer && rm packer_1.4.3_linux_amd64.zip && rmdir packer


# Enable this RUN statement when you need to connect to the VRDP server of the VM to troubleshoot issues
#RUN VBOXVER=$(wget -qO - https://download.virtualbox.org/virtualbox/LATEST.TXT) && \
#    wget "https://download.virtualbox.org/virtualbox/${VBOXVER}/Oracle_VM_VirtualBox_Extension_Pack-${VBOXVER}.vbox-extpack" && \
#    VBoxManage extpack install --accept-license=56be48f923303c8cababb0bb4c478284b688ed23f16d775d729b89a2e8e5f9eb Oracle_VM_VirtualBox_Extension_Pack-${VBOXVER}.vbox-extpack && \
#    rm Oracle_VM_VirtualBox_Extension_Pack-${VBOXVER}.vbox-extpack


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
