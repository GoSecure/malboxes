
# This disables Tamper Protection introduced in Windows 10 1903 (May 2019 Update)
# but it requires us to run disable_defender_tamper_protection.ps1 beforehand to allow registry changes
Set-ItemProperty -Path "HKLM:\Software\Microsoft\Windows Defender\Features" -Name "TamperProtection" -Value 0

# Disable Windows Defender on Windows 10
Set-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows Defender" -Name "DisableAntiSpyware" -Value 1
Set-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows Defender" -Name "DisableRoutinelyTakingAction" -Value 1

# Disable Windows Defender cloud protection and automatic sample submission
$spynet = "HKLM:\Software\Policies\Microsoft\Windows Defender\Spynet"

If (!(Test-Path $spynet)) {
    New-Item -Path $spynet -Force | Out-Null
}

Set-ItemProperty -Path $spynet -Name "SpynetReporting" -Type DWord -Value 0
Set-ItemProperty -Path $spynet -Name "SubmitSamplesConsent" -Type DWord -Value 2