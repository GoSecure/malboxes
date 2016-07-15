# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
	config.vm.box = "{{ profile }}"
	config.vm.provider "virtualbox" do |vb|
		vb.name = "{{ name }}"
		vb.gui = true
	end

	# Host files are shared on the Desktop
	config.vm.synced_folder ".", "/Users/{{ username }}/Desktop/host"
end
