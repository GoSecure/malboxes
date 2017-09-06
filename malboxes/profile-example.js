{
    "package": [{"package": "thunderbird"}],
    "document": [{"modtype": "add", "docpath": "C:\\Test.doc"}],
    "directory": [{"modtype": "add", "dirpath": "C:\\mlbxs\\"}],
    "registry": [
        {"modtype": "add", "key": "HKLM:\\Hardware\\Description\\System", "value": "04/04/04", "name": "SystemBiosDate", "valuetype": "String"},
        {"modtype": "add", "key": "HKLM:\\Hardware\\Description\\System", "value": "Hardware Version 0.0 PARTTBLX", "name": "SystemBiosDate", "valuetype": "String"},
        {"modtype": "delete", "key": "HKLM:\\HARDWARE\\ACPI\\DSDT", "name": "VBOX__"},
        {"modtype": "delete", "key": "HKLM:\\HARDWARE\\ACPI\\FADT", "name": "VBOX__"},
        {"modtype": "delete", "key": "HKLM:\\HARDWARE\\ACPI\\RSDT", "name": "VBOX__"},
        {"modtype": "delete", "key": "HKLM:\\SYSTEM\\ControlSet001\\Services", "name": "VBoxGuest"},
        {"modtype": "delete", "key": "HKLM:\\SYSTEM\\ControlSet001\\Services", "name": "VBoxMouse"},
        {"modtype": "delete", "key": "HKLM:\\SYSTEM\\ControlSet001\\Services", "name": "VBoxService"},
        {"modtype": "delete", "key": "HKLM:\\SYSTEM\\ControlSet001\\Services", "name": "VBoxSF"},
        {"modtype": "delete", "key": "HKLM:\\SYSTEM\\ControlSet001\\Services", "name": "VBoxVideo"},
        {"modtype": "add", "key": "HKLM:\\HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0", "value": "Malboxes", "name": "Identifier", "valuetype": "String"}],
    "packer": {
        "_comment": "See https://www.packer.io/docs/templates/provisioners.html for syntax"
        "provisioners": [
            {
                "type": "powershell",
                "inline": ["dir c:\\"]
            }
        ]
    }
}
