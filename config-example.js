{
	/*
	 * Malboxes Example Configuration File
	 *
	 * Uncomment a specific section of the file to trigger a particular feature.
     *
     * Paths should be written using forward slashes even on Windows.
     * For ex: C:/Tools
	 */

	// This allows you to use a local filestore for ISOs.
	// For all versions of Windows except Windows 10 you will need this.
	// "iso_path": "/path/to/your/windows/isos/",

	// Trial or registered version?
	// If using a registered product update the product_key and set trial to 'false'.
	// See https://github.com/GoSecure/malboxes/blob/master/docs/windows-licenses.adoc for more information.
	"trial": "true",
	//"trial": "false",
	//"product_key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",

	// VM settings
	"username": "malboxes",
	"password": "malboxes",
	"computername": "dirty",

	// Windows Defender: true means enabled, false means disabled. Default is false.
	//"windows_defender": "false",
	// Windows Updates: true means enabled, false means disabled. Default is false.
	//"windows_updates": "false",

	// Chocolatey packages to install on the VM
	"choco_packages": "sysinternals dependencywalker windbg wireshark 7zip putty fiddler processhacker regshot apm",

	// Setting the IDA Path will copy the IDA remote debugging tools into the guest
	//"ida_path": "/path/to/your/ida",

	// Setting Tools Path will copy all the files under the given path into the guest.
	// Useful to copy proprietary or unpackaged tools.
	// Note: packer's file provisonning is really slow, avoid having more than
	// 100 megabytes in there.
	//"tools_path": "/path/to/your/tools",

	"_comment": "last line must finish without a comma for file to be valid json"
}
