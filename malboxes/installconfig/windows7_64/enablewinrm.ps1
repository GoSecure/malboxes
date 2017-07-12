# We need to wait for the network to come up before we can attempt to change its settings
# See gh#60
Start-Sleep -s 45

# --------------------------------------------------------------------------------------------------------------------
# Enclosed section comes from the packer-windows project
# https://github.com/joefitzgerald/packer-windows/blob/a2b9d6fdd91a857d605fb1d7ec822f3fdfa71db4/scripts/fixnetwork.ps1
# Licensed under the MIT License
# Copyright (c) 2014 Joe Fitzgerald

# You cannot enable Windows PowerShell Remoting on network connections that are set to Public
# Spin through all the network locations and if they are set to Public, set them to Private
# using the INetwork interface:
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa370750(v=vs.85).aspx
# For more info, see:
# http://blogs.msdn.com/b/powershell/archive/2009/04/03/setting-network-location-to-private.aspx

# Network location feature was only introduced in Windows Vista - no need to bother with this
# if the operating system is older than Vista
if([environment]::OSVersion.version.Major -lt 6) { return }

# You cannot change the network location if you are joined to a domain, so abort
if(1,3,4,5 -contains (Get-WmiObject win32_computersystem).DomainRole) { return }

# Get network connections
$networkListManager = [Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]"{DCB00C01-570F-4A9B-8D69-199FDBA5723B}"))
$connections = $networkListManager.GetNetworkConnections()

$connections |foreach {
	Write-Host $_.GetNetwork().GetName()"category was previously set to"$_.GetNetwork().GetCategory()
	$_.GetNetwork().SetCategory(1)
	Write-Host $_.GetNetwork().GetName()"changed to category"$_.GetNetwork().GetCategory()
}
# --------------------------------------------------------------------------------------------------------------------

winrm quickconfig -q -transport:http
winrm set winrm/config/client '@{AllowUnencrypted="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
# .Net 4.0 installer (a choco dep) fails w/o this amount of memory (#31)
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="800"}'
net stop winrm
netsh advfirewall firewall set rule group="remote administration" new enable=yes
netsh firewall add portopening TCP 5985 "Port 5985"
# oddly enough the space is required below
sc.exe config winrm start= auto
net start winrm
