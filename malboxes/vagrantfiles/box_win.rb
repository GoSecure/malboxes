Vagrant.configure(2) do |config|
	config.vm.guest = :windows
	config.vm.communicator = :winrm
	config.winrm.username = "{{ username }}"
	config.winrm.password = "{{ password }}"

	# Giving plenty of times for updates
	config.vm.boot_timeout = 600
	config.vm.graceful_halt_timeout = 600
end
