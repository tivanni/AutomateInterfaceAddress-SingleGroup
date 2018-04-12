#!/usr/bin/python


### The script automatically configures ip addresses on network devices
### The script is made for configuring networks with point-to-point connections, each interface receives a /30 address
### The script assumes device's hostname is made by one character and one number. The character identify the group, the number the ID of the device. NB: ID has to be between 0 and 9. Example: hostname is R1
### The addresses are chosen using a convention. The four octets that made the ip address are selected in the following way
### The first two octets are assigned per Group. Groups info are read from file group_addresses. Example: device R6 is in group R, group R has first two octets 172.16
### The third octet is chosen comparing the devices's ID. For each connection, the two IDs are concatenated, with the smaller one in first position. Example: connection R2 <-> R5, third octet is 25
### The fourth octet is chosen comparing the devices's ID as well. The device with smaller device ID has fourth octet equal to 1, the other device has fourth octet equals to 2
### Example: R2 interface Fa0/0 is connected to R3 interface Fa1/1. Group R has assigned address group "172.16". R2 Fa0/0 gets ip 172.16.23.1, R3 Fa1/1 gets ip 172.16.23.2
### Each switch has to have at least one interface with a reachable address configured (usually, a management interface). Telnet connections have to be allowed and configured. CDP has to be enabled
### The hostname and the management ip address of each switch has to be specified in the file group_addresses.conf, in the form "hostname mgmt_ip", one device per line.
### NB: cdp has to be disabled on the interface used for the management of the switch (no cdp enable)
### The script is developed for Cisco 2961. FastEth 0/0 and 0/1 are L3 and shut down by default. FastEth 1/X are L2 and no shut by default


import pexpect
import getpass

###Creating Dictionary for Devices and Groups
devices = {}
groups = {}

###Reading the config files
file_devices = open('devices.conf')
group_addresses = open("group_addresses.conf")

###reading devices file and insert values in the dictionary "devices"
for line in file_devices:
    line_fields = line.split()
    hostname = line_fields[0]
    ip = line_fields[1]
    devices[hostname]=ip

###reading groups file and insert values in the dictionary "groups"
for line in group_addresses:
    line_fields = line.split()
    group = line_fields[0]
    base_address = line_fields[1]
    groups[group] = base_address


###connect to each device and configure the ip addresses
hostnames = devices.keys()

for hostname in hostnames:
    HOST_IP = devices[hostname]
    ###The Group of the hostname is the first letter of the hostname. Example: the Group of R5 is R
    local_hostname_group = hostname[0]
    ###ID of the  hostname is the number after the group. Example: R5 ID is 5. NB: devices must have ID between 0 and 9
    local_hostname_id = hostname[1]
    user = "admin"
    password = "password"
    ###Define possible prompts
    ###NB: parenthesis have to be escaped
    prompt_global = hostname + "#"
    prompt_config_mode = hostname + "\(config\)#"
    prompt_config_interface = hostname + "\(config-if\)#"
    ###connect to the switch
    print "accessing host '"+hostname+"', management ip: "+HOST_IP
    child = pexpect.spawn('telnet ' + HOST_IP)
    child.expect('Username: ')
    child.sendline(user)
    child.expect('Password: ')
    child.sendline(password)
    child.expect(prompt_global)
    ###Sending Terminal lenght 0, if the output of the commands executed later is long, is not required to press multiple time "space" or "enter" to view all the output
    child.sendline('terminal length 0')
    child.expect(prompt_global)
    child.sendline('show cdp neighbors')
    child.expect(prompt_global)
    ###Reading the output of command executed.Output is in the following form
    '''R4#show cdp neighbors
    Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater

    Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
    R2               Fas 1/0            147        R S I      2691      Fas 1/1
    R3               Fas 1/1            123        R S I      2691      Fas 1/1
    R1               Fas 0/1            135        R S I      2691      Fas 1/1
    '''
    cdp_output = child.before

    ###split output in lines
    cdp_output_lines = cdp_output.split("\n")
    ###Check line by line
    for line in cdp_output_lines:
        line=line.strip() ###removes carriege return and similar characters
        if(line): ###check line is not empty
            line_fields = line.split()
            first_field=line_fields[0]
            ###If the first field in the line is a neighbor of a valid device in the the network, proceed with configuration
            if(devices.has_key(first_field)):
                remote_hostname = first_field
                ###The Group of the hostname is the first letter of the hostname. Example: the Group of R5 is R
                remote_hostname_group = remote_hostname[0]
                ###ID of the  hostname is the number after the group. Example: R5 ID is 5. NB: devices must have ID between 0 and 9
                remote_hostname_id = remote_hostname[1]
                local_interface=line_fields[1] + " " + line_fields[2]
                '''
                ###At the moment, not required to parse the remote interface
                ###Remote interface is made by the last two items in the line. Line doesn't have always the same number of field,better to reverse the line and take the first two fields
                line_fields.reverse()
                remote_interface = line_fields[1] + " " + line_fields[0]
                print "remote interface " + remote_interface
                '''
                print "Device " + hostname + ", interface " + local_interface + " remote Device " + remote_hostname
                ###At this stage,configuration is supported only for devices in the same group. Support for configuration for devices in different groups will be added later
                if(local_hostname_group == remote_hostname_group):
                    if(local_hostname_id > remote_hostname_id):
                        ###Applying rules of the chosen convention
                        third_octect = remote_hostname_id + local_hostname_id
                        fourth_octect = "2"
                    else:
                        ###Applying rules of the chosen convention
                        third_octect= local_hostname_id + remote_hostname_id
                        fourth_octect = "1"
                    ip_address = groups[local_hostname_group] + third_octect + "." + fourth_octect

                    ###Starting config of the interface
                    child.sendline('configure terminal')
                    child.expect(prompt_config_mode)
                    child.sendline('interface ' + local_interface)
                    child.expect(prompt_config_interface)
                    ###On Cisco 2961,interfaces Fa0/0 and Fa0/1 are in L3 and shut down by default
                    if(local_interface == "Fas 0/0" or local_interface == "Fas 0/1"):
                        child.sendline('ip address ' + ip_address + " 255.255.255.252")
                        child.expect(prompt_config_interface)
                        child.sendline('no shutdown')
                        child.expect(prompt_config_interface)
                        child.sendline('end')
                        child.expect(prompt_global)
                    ###On Cisco 2961, interfaces Fa1/X are in L2 and up by default
                    else:
                        child.sendline('no switchport')
                        child.expect(prompt_config_interface)
                        child.sendline('ip address ' + ip_address + " 255.255.255.252")
                        child.expect(prompt_config_interface)
                        child.sendline('end')
                        child.expect(prompt_global)
                    print "configured ip address " + ip_address

    ###Save config at the end
    child.sendline('write mem')
    child.expect(prompt_global)
    print "Device " + hostname + ", config saved\n\n"






