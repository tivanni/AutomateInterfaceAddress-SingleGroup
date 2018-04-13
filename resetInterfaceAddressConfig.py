#!/usr/bin/python
import pexpect
import getpass

###Creating Dictionary for Devices and Groups
devices = {}

###Reading the config files
file_devices = open('devices.conf')

###reading devices file and insert values in the dictionary "devices"
for line in file_devices:
    line_fields = line.split()
    hostname = line_fields[0]
    ip = line_fields[1]
    devices[hostname]=ip

###Define username and password to be used for telnet
user = "admin"
password = "password"

###connect to each device and reset the ip addresses and the config on the interfaces with cdp enabled
hostnames = devices.keys()

for hostname in hostnames:
    HOST_IP = devices[hostname]
    print "accessing host '"+hostname+"', management ip: "+HOST_IP
    ###Define possible prompts
    ###NB: parenthesis have to be escaped
    prompt_global = hostname + "#"
    prompt_config_mode = hostname + "\(config\)#"
    prompt_config_interface = hostname + "\(config-if\)#"
    prompt_config_interface_range = hostname + "\(config-if-range\)#"
    ###Start telnet connection
    child = pexpect.spawn('telnet ' + HOST_IP)
    child.expect('Username: ')
    child.sendline(user)
    child.expect('Password: ')
    child.sendline(password)
    child.expect(prompt_global)
    ###Sending Terminal lenght 0, if the output of the commands executed later is long, is not required to press multiple time "space" or "enter" to view all the output
    child.sendline('terminal length 0')
    child.expect(prompt_global)
    child.sendline('show ip interface brief')
    child.expect(prompt_global)
    ###Reading the output of command executed.Output is in the following form
    '''R1#show ip interface brief
    Interface                  IP-Address      OK? Method Status                Protocol
    FastEthernet0/0            192.168.27.1    YES NVRAM  up                    up
    Serial0/0                  unassigned      YES NVRAM  administratively down down
    FastEthernet0/1            unassigned      YES manual administratively down down
    Serial0/1                  unassigned      YES NVRAM  administratively down down
    FastEthernet1/0            unassigned      YES unset  up                    up
    FastEthernet1/1            172.16.14.1     YES NVRAM  up                    up
    FastEthernet1/2            unassigned      YES unset  up                    down
    FastEthernet1/3            unassigned      YES unset  up                    down
    FastEthernet1/4            unassigned      YES unset  up                    down
    FastEthernet1/5            unassigned      YES unset  up                    down
    FastEthernet1/6            unassigned      YES unset  up                    down
    FastEthernet1/7            unassigned      YES unset  up                    down
    FastEthernet1/8            unassigned      YES unset  up                    down
    FastEthernet1/9            unassigned      YES unset  up                    down
    FastEthernet1/10           unassigned      YES unset  up                    down
    FastEthernet1/11           unassigned      YES unset  up                    down
    FastEthernet1/12           unassigned      YES unset  up                    down
    FastEthernet1/13           unassigned      YES unset  up                    down
    FastEthernet1/14           unassigned      YES unset  up                    down
    FastEthernet1/15           unassigned      YES unset  up                    down
    '''
    ip_interface_brief_output = child.before
    ###split output in lines
    ip_interface_brief_lines = ip_interface_brief_output.split("\n")
    ###Check line by line
    for line in  ip_interface_brief_lines:
        line = line.strip()  ###removes carriege return and similar characters
        if (line):  ###check line is not empty
            line_fields = line.split()
            first_field = line_fields[0]
            if ("Ethernet" in first_field):
                interface = first_field
                interface_address = line_fields[1]
                if not (interface == "FastEthernet0/0" or interface_address == "unassigned"): ###FastEthernet0/0 is used as management, address doens't have to be removed on it
                    child.sendline('configure terminal')
                    child.expect(prompt_config_mode)
                    child.sendline('interface ' + interface)
                    child.expect(prompt_config_interface)
                    ###On Cisco 2961,interfaces Fa0/0 and Fa0/1 are in L3, the interfaces are left up
                    if (interface == "Fas 0/1"):
                        child.sendline('no ip address')
                        child.expect(prompt_config_interface)
                        child.sendline('end')
                        child.expect(prompt_global)
                    ###On Cisco 2961, interfaces Fa1/X are in L2 and up by default
                    else:
                        child.sendline('no ip address')
                        child.expect(prompt_config_interface)
                        child.sendline('switchport')
                        child.expect(prompt_config_interface)
                        child.sendline('end')
                        child.expect(prompt_global)
                    print "Device " + hostname + ",reset execute on interface " + interface
    ###Clear cdp table
    child.sendline('clear cdp table')
    child.expect(prompt_global)
    ###Save config at the end
    child.sendline('write mem')
    child.expect(prompt_global)
    print "Device " + hostname + ", config saved\n\n"








