# Set UAC to default level (so Edge can be used from account)
# Note: a restart is required
$Path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
Set-ItemProperty -Path $Path -Name ConsentPromptBehaviorAdmin -Value 5 -Type "Dword"
Set-ItemProperty -Path $Path -Name PromptOnSecureDesktop -Value 1 -Type "Dword"
Set-ItemProperty -Path $Path -Name EnableLUA -Value 1 -Type "Dword"
