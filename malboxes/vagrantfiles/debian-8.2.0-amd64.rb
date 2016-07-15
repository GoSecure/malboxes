Vagrant.configure(2) do |config|
  config.vm.box = "debian820"
  config.vm.guest = :linux
  config.vm.boot_timeout = 1 
  
  config.vm.provider "virtualbox" do |vb|
	vb.name = "debian820"
	vb.gui = true
	vb.customize ["modifyvm", :id, "--nic1", "intnet"]
	vb.customize ["modifyvm", :id, "--intnet1", "malwarelab"]
  end
end
