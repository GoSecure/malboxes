Vagrant.configure(2) do |config|
	config.vm.box = "win7x64"
	config.vm.guest = :windows
	config.vm.boot_timeout = 1

	config.vm.provider "virtualbox" do |vb|
		vb.name = "win81x64"
		vb.gui = true
		vb.customize ["modifyvm", :id, "--nic1", "intnet"]
		vb.customize ["modifyvm", :id, "--intnet1", "malwarelab"] # need to change that
		vb.customize ["modifyvm", :id, "--vram", "32"]
		# vb.customize ["modifyvm", :id, "--draganddrop", "hosttoguest"]
		# config.vm.provision "shell",
		# inline: "New-PSDrive -Name \"V\" -PSProvider FileSystem -Root \"\\\\VBOXSVR\\vagrant\" -Persist"
	end
end
