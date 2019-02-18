# Change the network types of the WinRM rules for public
netsh advfirewall firewall set rule name="Windows Remote Management (HTTP-In)" new profile=public