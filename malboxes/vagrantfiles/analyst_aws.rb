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

    # Giving plenty of times for updates
	config.vm.boot_timeout = 600
	config.vm.graceful_halt_timeout = 600

    #Configuration information for AWS
    config.vm.provider :aws do |aws, override|
        aws.access_key_id = "{{ aws_access_key }}"
        aws.secret_access_key = "{{ aws_secret_key }}"
        aws.instance_type = "m3.medium"
        aws.security_groups = "{{ aws_security_group }}"
        aws.keypair_name = "{{ aws_keypair }}"
        aws.ami = "{{ aws_ami_id }}"
        aws.tags = {
            'Name' => "Malboxes",
            'Template' => "{{ template_name }}"
          }
    end
end