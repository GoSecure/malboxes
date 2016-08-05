# Disables Automatic Updates on Windows 10
# Credit: https://4sysops.com/archives/disable-windows-10-update-in-the-registry-and-with-powershell/

# Setup
$WindowsUpdatePath = "HKLM:SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\"
$AutoUpdatePath = "HKLM:SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
If(Test-Path -Path $WindowsUpdatePath) {
    Remove-Item -Path $WindowsUpdatePath -Recurse
}
New-Item -Path $WindowsUpdatePath
New-Item -Path $AutoUpdatePath

# Never check for updates
Set-ItemProperty -Path $AutoUpdatePath -Name NoAutoUpdate -Value 1

# Notify for download and notify for install
#Set-ItemProperty -Path $AutoUpdatePath -Name NoAutoUpdate -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name AUOptions -Value 2
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallDay -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallTime -Value 3

# Auto download and notify for install
#Set-ItemProperty -Path $AutoUpdatePath -Name NoAutoUpdate -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name AUOptions -Value 3
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallDay -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallTime -Value 3

# Auto download and schedule the install
#Set-ItemProperty -Path $AutoUpdatePath -Name NoAutoUpdate -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name AUOptions -Value 4
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallDay -Value 0
#Set-ItemProperty -Path $AutoUpdatePath -Name ScheduledInstallTime -Value 3
