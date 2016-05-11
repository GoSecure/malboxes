Vagrant.configure(2) do |config|
	config.vm.box = "win7_32_analyst"
	config.vm.guest = :windows
	config.vm.boot_timeout = 1

	config.vm.provider "virtualbox" do |vb|
		vb.name = "win7dirty"
		vb.gui = true
		vb.customize ["modifyvm", :id, "--vram", "32"]
		vb.customize ["modifyvm", :id, "--draganddrop", "hosttoguest"]
	end
end
