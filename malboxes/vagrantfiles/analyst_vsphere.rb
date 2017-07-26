-*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
       # config.vm.box = "win10_64_analyst"
       config.vm.box = 'dummy'
       config.vm.box_url = 'vsphere-dummy.box'
       config.vm.provider :vsphere do |vsphere|
       # The vSphere host we're going to connect to
       vsphere.host = {{ vsphere_host }}
       vsphere.compute_resource_name = {{ remote_host }}
       vsphere.clone_from_vm = {{ vsphere_clone_from_vm }}
       vsphere.name =  {{ vsphere_name }}
       vsphere.user = {{ vsphere_user}}
       vsphere.password = {{ vsphere_password }}
       vsphere.insecure = {{ vsphere_insecure }}
end

       # Host files are shared on the Desktop
       config.vm.synced_folder ".", "/Users/malboxes/Desktop/host"
end
~
~
