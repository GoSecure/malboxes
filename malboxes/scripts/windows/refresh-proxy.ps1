# Windows...
#
# Here is a note to someone wondering what we're doing _here_
# (And why we're doing it here and now)
#
# Windows7 supports proxy configuration through Autounattend.xml
# Unattended install sets everything needed to have a system-wide proxy
# configuration.
#
# The problem seems to be that it fails to notify wininet subsystems of the
# configuration. Which can prevent us from accessing the Internet.
# (sometimes or always, it depends, I don't really know)
#
# This piece of code can't be run through WinRM for some reason. Running it
# through WinRM will result in Windows removing `ProxyEnable` and `ProxyServer`
# keys from the registry <--- O_o
#
# Anyway, in order to MakeItWork(tm) we need to run this interactively.
#
# These dark spells of black witchcraftery should be enough to allow
# Windows/IE/Wininet/Whatever to get the right memo and use the configured
# proxy
#

echo "Proxy is: $([Net.GlobalProxySelection]::Select.Address.Host)"

$signature = @'
[DllImport("wininet.dll", SetLastError = true, CharSet=CharSet.Auto)]
public static extern bool InternetSetOption(IntPtr hInternet, int dwOption, IntPtr lpBuffer, int dwBufferLength);
'@
$wininet = Add-Type -MemberDefinition $signature -Name wininet -Namespace pinvoke -PassThru

function Refresh-System
{
    $INTERNET_OPTION_SETTINGS_CHANGED   = 39
    $INTERNET_OPTION_REFRESH            = 37
    $INTERNET_OPTION_PROXY_SETTINGS_CHANGED = 95
    $a = $wininet::InternetSetOption(0, $INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    $b = $wininet::InternetSetOption(0, $INTERNET_OPTION_PROXY_SETTINGS_CHANGED, 0, 0)
    $c = $wininet::InternetSetOption(0, $INTERNET_OPTION_REFRESH, 0, 0)
}

function Test-Connection
{
    $ie = New-Object -comobject InternetExplorer.Application;
    $ie.visible=$False;
    $ie.navigate('http://google.com');
    start-sleep -s 5;
    $ie.quit();
}

Refresh-System
Test-Connection

echo "Proxy is: $([Net.GlobalProxySelection]::Select.Address.Host)"
