# AutomateInterfaceAddress-SingleGroup
### The script automatically configures ip addresses on network devices 
### The script is made for configuring networks with point-to-point connections, each interface receives a /30 address 
### The script assumes device's hostname is made by one character and one number. The character identify the group, the number the ID of the device. NB: ID has to be between 0 and 9. Example: hostname is R1 
### The addresses are chosen using a convention. The four octets that made the ip address are selected in the following way 
### The first two octets are assigned per Group. Groups info are read from file group_addresses. Example: device R6 is in group R, group R has first two octets 172.16 
### The third octet is chosen comparing the devices's ID. For each connection, the two IDs are concatenated, with the smaller one in first position. Example: connection R2 &lt;-> R5, third octet is 25 
### The fourth octet is chosen comparing the devices's ID as well. The device with smaller device ID has fourth octet equal to 1, the other device has fourth octet equals to 2 
### Example: R2 interface Fa0/0 is connected to R3 interface Fa1/1. Group R has assigned address group "172.16". R2 Fa0/0 gets ip 172.16.23.1, R3 Fa1/1 gets ip 172.16.23.2 
### Each switch has to have at least one interface with a reachable address configured (usually, a management interface). Telnet connections have to be allowed and configured. CDP has to be enabled 
### The hostname and the management ip address of each switch has to be specified in the file group_addresses.conf, in the form "hostname mgmt_ip", one device per line. 
### NB: cdp has to be disabled on the interface used for the management of the switch (no cdp enable) 
### The script is developed for Cisco 2961. FastEth 0/0 and 0/1 are L3 and shut down by default. FastEth 1/X are L2 and no shut by default
