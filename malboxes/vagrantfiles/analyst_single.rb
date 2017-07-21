# -*- mode: ruby -*-
# vi: set ft=ruby :
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'

Vagrant.configure(2) do |config|
	config.vm.box = "{{ template_name }}"
	config.vm.provider "virtualbox" do |vb|
		vb.name = "{{ name }}"
		vb.gui = true
	end

	# Host files are shared on the Desktop
	config.vm.synced_folder ".", "/Users/{{ username }}/Desktop/host"
end
