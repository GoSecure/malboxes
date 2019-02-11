# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
    # Using dummy box with provider=aws metadata
    config.vm.box = "dummy"
    config.vm.box_url = "https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box"

    config.vm.guest = :windows
    config.vm.communicator = :winrm
    config.winrm.username = "{{ username }}"
    config.winrm.password = "{{ password }}"

    config.vm.provider :aws do |aws, override|
        aws.access_key_id = "{{ aws_access_key }}"
        aws.secret_access_key = "{{ aws_secret_key }}"
        aws.instance_type = "m3.medium"
        aws.security_groups = "{{ aws_security_group }}"
        aws.keypair_name = "{{ aws_keypair }}"
        # FIXME still experimenting with this one
        aws.terminate_on_shutdown = true
        aws.ami = "{{ aws_ami_id }}"
    end
end