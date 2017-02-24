// ChangeCategory.ps1
//
$NLMType = [Type]::GetTypeFromCLSID('DCB00C01-570F-4A9B-8D69-199FDBA5723B')
$INetworkListManager = [Activator]::CreateInstance($NLMType)

$NLM_ENUM_NETWORK_CONNECTED  = 1
$NLM_NETWORK_CATEGORY_PUBLIC = 0x00
$NLM_NETWORK_CATEGORY_PRIVATE = 0x01
$UNIDENTIFIED = "Unidentified network"

$INetworks = $INetworkListManager.GetNetworks($NLM_ENUM_NETWORK_CONNECTED)

foreach ($INetwork in $INetworks)
{
    $Name = $INetwork.GetName()
    $Category = $INetwork.GetCategory()

    if ($INetwork.IsConnected -and ($Category -eq $NLM_NETWORK_CATEGORY_PUBLIC) -and ($Name -eq $UNIDENTIFIED))
    {
        $INetwork.SetCategory($NLM_NETWORK_CATEGORY_PRIVATE)
    }
}

winrm quickconfig -q -transport:http
winrm set winrm/config/client '@{AllowUnencrypted="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
net stop winrm
netsh advfirewall firewall set rule group="remote administration" new enable=yes
netsh firewall add portopening TCP 5985 "Port 5985"
sc.exe config winrm start=auto
net start winrm
