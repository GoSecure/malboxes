function Add-Shortcut{
    param([string]$target_path, [string]$dest_path, [string]$arguments="");
    #Create new env varibles for quick use
    $env:DESKTOP = [Environment]::GetFolderPath('Desktop');
    $env:STARTMENU = [Environment]::GetFolderPath('StartMenu');
    $env:STARTUP = [Environment]::GetFolderPath('Startup');
    #Check if path to shortcut setted. If not - set path to Desktop
    if (-Not [System.IO.Path]::IsPathRooted($dest_path)){
        $dest_path = $env:USERPROFILE + "\\Desktop\\" + $dest_path;
    }
    #Create subdirectory if doesn't exist
    $_path=Split-Path $dest_path;
    if (-Not (Test-Path $_path)){
        mkdir -Force $_path;
    }
    #Check if target exist
    if (-Not (Test-Path $target_path)){
        Write-Output "[Add-Shortcut::Error] Can't add shortcut. Target path '$target_path' not found.";
        return;
    }
    #Check if shortcut exist
    if ((Test-Path $dest_path)){
        Write-Output "[Add-Shortcut::Error] Can't add shortcut. Destination path '$dest_path' exist.";
        return;
    }
    Write-Output "[Add-Shortcut] Destination: '$dest_path'; Target: '$target_path'";
    if((Get-Item $target_path) -is [System.IO.DirectoryInfo]){
        #Create shortcut (Symbolic link) for folder
        Start-Process "cmd.exe" -ArgumentList "/c mklink /D `"$dest_path`" `"$target_path`"" -Wait -NoNewWindow;      
    }else{
        #Create shortcut for file
        $_shell = New-Object -ComObject ("WScript.Shell");
        $_shortcut = $_shell.CreateShortcut($dest_path);
        $_shortcut.TargetPath=$target_path;
        if(-Not [String]::IsNullOrEmpty($arguments)){
            $_shortcut.Arguments=$arguments;
        }
        $_shortcut.WorkingDirectory=[System.IO.Path]::GetDirectoryName($target_path);
        $_shortcut.Save();
    }
}
