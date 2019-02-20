# Allow WinRM to communicate on public network
netsh advfirewall firewall add rule name="Public network WinRM" dir=in action=allow protocol=TCP localport=5985 profile=public