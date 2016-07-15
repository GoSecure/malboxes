Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
# The rule below doesn't work for Windows 7
# Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
