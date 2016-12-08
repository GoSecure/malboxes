iex ((New-Object Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# For some reason, AutoHotkey.portable wasn't working with WinPcap, so use the full installation
cinst autohotkey -y
$env:Path = "$($env:Path)C:\Program Files\AutoHotkey;" 
