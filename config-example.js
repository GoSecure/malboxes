{
	/*
	 * Malboxes Example Configuration File
	 *
	 * Uncomment a specific section of the file to trigger a particular feature.
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

	// VM username and password
	// TODO. It doesn't work now.
	//"username": "vagrant",
	//"password": "vagrant",

	// Setting the IDA Path will copy the IDA remote debugging tools into the guest
	//"ida_path": "/path/to/your/ida",

	// Setting Tools Path will copy all the files under the given path into the guest.
	// Useful to copy proprietary or unpackaged tools.
	//"tools_path": "/path/to/your/tools",

	"_comment": "last line must finish without a comma for file to be valid json"
}
