# switchinfo

A tool to show what is connected to switch ports

# Management commands

| Command                      | Description                                         |
|------------------------------|-----------------------------------------------------|
| switch_info [IP] [community] | Add a new switch with IP and SNMP community         |
| switch_update [switch]       | Update hostname and description for a switch        |
| load_arp [switch]            | Load ARP  from one or all switches                  |
| load_interfaces_rfc [switch] | Load interface information from one or all switches |
| load_mac [switch]            | Load MAC addresses from one or all switches         |
| load_vlans [switch]          | Load vlans from one or all switches                 |
| load_oui                     | Load MAC vendors from standards-oui.ieee.org        | 

The argument [switch] can be the name of a switch or the word "all" to run the command on all switches.

# Supported switch brands

All switches supporting IF-MIB should work, but some switches need some vendor-specific adaption.

The following brands are tested:

* Cisco
* HPE Aruba (CX and AOS-S)
* HP ProCurve (not able to get all information on all models)
* Fortinet
* Extreme Networks
* Korenix
* Westermo SDSL modems

