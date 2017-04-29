Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private

winrm quickconfig -q -transport:http
winrm set winrm/config/client '@{AllowUnencrypted="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
# .Net 4.0 installer (a choco dep) fails w/o this amount of memory (#31)
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="800"}'
net stop winrm
sc.exe config winrm start=auto
net start winrm
