iex ((New-Object Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

cinst sysinternals -y
cinst dependencywalker -y
cinst windbg -y

# For some reason, AutoHotkey.portable wasn't working with WinPcap, so use the full installation
cinst autohotkey -y
$env:Path = "$($env:Path)C:\Program Files\AutoHotkey;" 

cinst wireshark -y -i
cinst 7zip -y
cinst putty -y
cinst fiddler -y
cinst processhacker -y
cinst regshot -y
cinst apm -y
