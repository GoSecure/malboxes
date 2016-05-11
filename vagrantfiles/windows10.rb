Vagrant.configure(2) do |config|
	config.vm.box = "win10_64_analyst"
	config.vm.guest = :windows
	config.vm.boot_timeout = 1

	config.vm.provider "virtualbox" do |vb|
		vb.name = "win10victim"
		vb.gui = true
		vb.customize ["modifyvm", :id, "--vram", "32"]
		vb.customize ["modifyvm", :id, "--draganddrop", "hosttoguest"]
		#config.vm.provision "shell",
		#  inline: "New-PSDrive -Name \"V\" -PSProvider FileSystem -Root \"\\\\VBOXSVR\\vagrant\" -Persist"
	end
end
