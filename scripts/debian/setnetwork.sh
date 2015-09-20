#!/bin/bash

# Stop isc-dhcp-server from autostarting after install, as it will fail (no config)
echo exit 101 > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d

apt-get install -y isc-dhcp-server

cat << EOF > /etc/network/interfaces
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet static
	address 10.0.0.1
	netmask 255.255.255.0
EOF

ip addr add 10.0.0.1/24 dev eth0

systemctl disable dhclient
kill `pidof dhclient`

cat << EOF >> /etc/dhcp/dhcpd.conf
ddns-update-style none;
option domain-name "malwarelab.local";
option domain-name-servers 10.0.0.1;

subnet 10.0.0.0 netmask 255.255.255.0 {
	range 10.0.0.2 10.0.0.254;
}

subnet 10.0.2.0 netmask 255.255.255.0 {
}

EOF

rm /usr/sbin/policy-rc.d
systemctl start isc-dhcp-server
