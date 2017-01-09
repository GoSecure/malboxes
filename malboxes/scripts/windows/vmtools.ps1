$vboxAdditionsDrive = Get-WmiObject Win32_LogicalDisk -Filter "DriveType=5" |
			Where-Object { $_.VolumeName -Like '*VBOX*' } |
			Select -ExpandProperty DeviceID

# Starting with VirtualBox 5.1.12 the name of the certificate changed
$newCertName = "vbox-sha1.cer"
if (Test-Path "$vboxAdditionsDrive\cert\$newCertName") {
    &certutil -addstore -f "TrustedPublisher" "$vboxAdditionsDrive\cert\$newCertName"
}
else {
    &certutil -addstore -f "TrustedPublisher" "$vboxAdditionsDrive\cert\oracle-vbox.cer"
}
&"$vboxAdditionsDrive\VBoxWindowsAdditions.exe" /S
