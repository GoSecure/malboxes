$vboxAdditionsDrive = Get-WmiObject Win32_LogicalDisk -Filter "DriveType=5" |
			Where-Object { $_.VolumeName -Like '*VBOX*' } |
			Select -ExpandProperty DeviceID

&certutil -addstore -f "TrustedPublisher" "$vboxAdditionsDrive\cert\oracle-vbox.cer"
&"$vboxAdditionsDrive\VBoxWindowsAdditions.exe" /S
