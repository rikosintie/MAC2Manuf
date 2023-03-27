import hashlib
import json
import re
import sys

import manuf

# from icecream import ic


#  ic.enable()
# ic.disable()

'''
References:
https://github.com/wireshark/wireshark/blob/master/manuf
https://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python/6545090#6545090
https://stackoverflow.com/questions/20944483/python-3-sort-a-dict-by-its-values
https://docs.python.org/3.3/tutorial/datastructures.html
https://www.quora.com/How-do-I-write-a-dictionary-to-a-file-in-Python
https://www.programiz.com/python-programming/break-continue
https://www.ascii-art-generator.org/

read mac-addr.txt containing the output of
show mac add int g1/0/1 | i Gi
show mac add int g1/0/2 | i Gi
show mac add int g1/0/3 | i Gi
show mac add int g1/0/4 | i Gi

and create a list of Vlan, Mac Address, interface and manufacturer.

test-switch#show mac add int g1/0/1 | i Gi
  10    8434.97a7.708b    DYNAMIC     Gi1/0/1
test-switch#show mac add int g1/0/2 | i Gi
test-switch#show mac add int g1/0/3 | i Gi
  10    0c4d.e9c1.4a0d    DYNAMIC     Gi1/0/3
test-switch#show mac add int g1/0/4 | i Gi

Output
Number Entries: 65

Vlan     MAC Address      Interface
  10    8434.97a7.708b     Gi1/0/1   HewlettP
--------------------------------------------------
  10    0c4d.e9c1.4a0d     Gi1/0/3   Apple
--------------------------------------------------

Uses the Parser library for Wireshark's OUI database from
https://github.com/coolbho3k/manuf to convert the MAC to a manufacture.
The database needs to be updated occaisionally using:

python3 manuf.py -u


Changelog
March 7, 2018
Added code to read Mac2IP.json and use it as a dictionary of IP to MAC.
Mac2IP.json is created by running arp.py against the output
"show ip arp" or "sh ip arp vlan x" on a core switch
if Mac2IP.json is found in the same directory as macaddr.py it adds the
IP address to the output.
if Mac2IP.json is not found the IP address is not added
Vlan     MAC Address      Interface      IP           Vendor
   20    f8b1.56d2.3c13     Gi1/0/3   10.129.20.70    Dell
 ----------------------------------------------------------------
   20    0011.431b.b291     Gi1/0/16   10.129.20.174    Dell
 ----------------------------------------------------------------

March 24, 2018
Added an MD5 hash function to the list of MAC addresses. This gives a
quick comparison of the before
and after is some cables got swapped but are on the correct vlan.
Added a sorted output of the MAC addresses. If there are differences
before and after you can save the list of MACs and use MELD or Notepad++
(with the compare plugin) to see what is different.

Hash of all the MAC addresses
6449620420f0d67bffd26b65e9a824a4

Sorted list of MAC Addresses
0018.c840.1295
0018.c840.12a8
0027.0dbd.9f6e

April 7, 2018
Added output for PingInfoView (nirsoft.net)

PingInfo Data
10.56.238.150 b499.ba01.bc82
10.56.239.240 0026.5535.7b7a

April 30, 2018
Added better error trapping for the json and mac-addr.txt.
Stopped stripping DYNAMIC and STATIC from the input.

May 15, 2018
Fixed a bug in the IP address selection loop. I wasn't clearing IP_Data at the
end of the loop so is an interface didn't have an IP address in the json file
it would use the last IP address.

Clear the IP address in case the next interface has a MAC but no IP address
    IP_Data = ''
'''

vernum = '1.1'
AsciiArt = '''
 __  __    _    ____   ____    __  __                    __            _
|  \/  |  / \  / ___| |___ \  |  \/  | __ _ _ __  _   _ / _| __ _  ___| |_
| |\/| | / _ \| |       __) | | |\/| |/ _` | '_ \| | | | |_ / _` |/ __| __|
| |  | |/ ___ \ |___   / __/  | |  | | (_| | | | | |_| |  _| (_| | (__| |_
|_|  |_/_/   \_\____| |_____| |_|  |_|\__,_|_| |_|\__,_|_|  \__,_|\___|\__|
'''


def version():
    """
    This function prints the version of this program. It doesn't allow
    any argument.
    """
    print(AsciiArt)
    print("+----------------------------------------------------------------+")
    print("| " + sys.argv[0] + " Version " + vernum + "                                      |")
    print("| This program is free software; you can redistribute it         |")
    print("| and/or modify it in any way you want. If you improve           |")
    print("| it please send me a copy at the email address below.           |")
    print("|                                                                |")
    print("|                                                                |")
    print("| Author: Michael Hubbard, michael.hubbard999@gmail.com          |")
    print("|         mwhubbard.blogspot.com                                 |")
    print("|         @rikosintie                                            |")
    print("+----------------------------------------------------------------+")


version()

#  https://stackoverflow.com/questions/11006702/elegant-format-for-a-mac-address-in-python-3-2


def format_mac(mac: str) -> str:
    """Converts most common MAC address formats
    into aa:bb:cc:dd:ee:ff format

    '008041aefd7e',  # valid
    '00:80:41:ae:fd:7e',  # valid
    '00:80:41:AE:FD:7E',  # valid
    '00:80:41:aE:Fd:7E',  # valid
    '00-80-41-ae-fd-7e',  # valid
    '0080.41ae.fd7e',  # valid
    '00 : 80 : 41 : ae : fd : 7e',  # valid
    '  00:80:41:ae:fd:7e  ',  # valid
    '00:80:41:ae:fd:7e\n\t',  # valid

    'aa:00:80:41:ae:fd:7e',  # invalid
    '0:80:41:ae:fd:7e',  # invalid
    'ae:fd:7e',  # invalid
    '$$:80:41:ae:fd:7e',  # invalid

    Args:
        mac (str): A valid mac address format

    Returns:
        str: MAC in aa:bb:cc:dd:ee:ff format
    """
    mac = re.sub('[.:-]', '', mac).lower()  # remove delimiters, convert to lc
    mac = ''.join(mac.split())  # remove whitespaces
    assert len(mac) == 12  # length should be now exactly 12 (eg. 008041aefd7e)
    assert mac.isalnum()  # should only contain letters and numbers
    # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
    mac = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
    return mac

# MAC addresses are expressed differently depending on the
# manufacture and even model device
# the formats that this script can parse are:
# 0a:0a:0a:0a:0a:0a, 0a-0a-0a-0a-0a-0a, 0a0a0a.0a0a0a0 and 0a0a0a-0a0a0a
# this should cover most Cisco and HP devices.
#


print()
# create an empty dictionary to hold the mac-IP data
Mac_IP = {}
IP_Data = ''
device_name = ''
# create an empty list to hold MAC addresses for hashing
hash_list = []
# open the json created by arp.py if it exists
my_json_file = 'Mac2IP.json'
try:
    with open(my_json_file) as f:
        Mac_IP = json.load(f)
except FileNotFoundError as fnf_error:
    print(fnf_error)
    print('IP Addresses will not be included')
    my_json_file = None
p = manuf.MacParser()
# create a blank list to accept each line in the file
data = []
mydatafile = 'mac-addr-cx.txt'
try:
    f = open(mydatafile, 'r')
except FileNotFoundError as fnf_error:
    print(fnf_error)
    sys.exit(0)
else:
    for line in f:
        match_PC = re.search(r'([0-9A-F]{2}[-:]){5}([0-9A-F]{2})', line, re.I)
        match_Cisco = re.search(r'([0-9A-F]{4}[.]){2}([0-9A-F]{4})', line, re.I)
        match_HP = re.search(r'([0-9A-F]{6}[-])([0-9A-F]{6})', line, re.I)
        # strip out lines without a mac address
        if match_PC or match_Cisco or match_HP:
            data.append(line)
        device_name_loc = line.find('#')
        if device_name_loc != -1:
            device_name = line[0:device_name_loc]
            device_name = device_name.strip()
    f.close
try:
    save_device = device_name + "-macs.txt"
    device_file = open(save_device, 'w')
    for line in data:
        device_file.write(line)
    device_file.close()
except FileNotFoundError as fnf_error:
    print(fnf_error)
    sys.exit(0)


ct = len(data)-1
counter = 0
IPs = []
print()
print(f'Device Name: {device_name}')
print()
print('PingInfo Data')
while counter <= ct:
    IP = data[counter]
    IP_test = IP.split()
    #ic(IP_test)
# Remove newline at end
    IP = IP.strip('\n')
#   The Nexus line adds an * and spaces to the front of the line
    IP = IP.strip('*    ')
#   The Nexus line includes additional fields that need to be stripped
    IP = IP.replace('  0         F      F   ', '')
    IP = IP.replace('    ~~~      F    F ', '')
# extract MAC Address and save to hash_list for hashing
    L = str.split(IP)
    #ic(L)
    Vlan = L[1]
    Mac = L[0]
    # convert cisco format to aruba format
    Mac = format_mac(Mac)
    # Mac_Type = L[2]
    # ic(Mac_Type)
    # Interface_Num = L[3]
    Interface_Num = L[3]

# The interface isn't in the same location in the output on all switches
# This loop seaches for a / in the value before picking the interface.
# Old method *******************************************
#    if Interface_Num.find('/') == -1:
#        Interface_Num = L[5]
# ******************************************************
    ct2 = len(L)
    count2 = 2
    while count2 < ct2:
        Interface_Num = L[count2]
        #ic(Interface_Num)
        if Interface_Num.find('/') == -1:
            count2 += 1
            # print(Interface_Num) uncomment if interface doesn't print
        else:
            break
#            continue
    temp = hash_list.append(Mac)
    if Mac in Mac_IP:
        IP_Data = Mac_IP[Mac]
    else:
        IP_Data = 'No-Match'
#       print the pinginfo data
    print(IP_Data, Mac)
# pull the manufacturer with manuf
    manufacture = p.get_manuf(Mac)
# Pad with spaces for output alignment
    Front_Pad = 4 - len(Vlan)
    Pad = 7 - len(Vlan) - Front_Pad
    Vlan = (' ' * Front_Pad) + Vlan + (' ' * Pad)
# Pad MAC Address Field
    Pad = 18 - len(Mac)
    Mac = Mac + (' ' * Pad)
# Pad type field
    # Pad = 11 - len(Mac_Type)
    # Mac_Type = Mac_Type + (' ' * Pad)
# Pad Interface
    Pad = 12 - len(Interface_Num)
    Interface_Num = Interface_Num + (' ' * Pad)
# Pad IP address field if the json file exists
    if my_json_file:
        Pad = 17 - len(IP_Data)
        IP_Data = IP_Data + (' ' * Pad)
# create the separator at 80 characters
        Pad = '--' * 40
    else:
        # if not create the separator at 60 characters since there won't be IPs
        Pad = '--' * 30
# Build the string
    # IP = Vlan + IP_Data + Mac + Mac_Type + Interface_Num + str(manufacture)
    IP = Vlan + IP_Data + Mac + "  " + Interface_Num + str(manufacture)
    IPs.append(str(IP))
#    IPs.append('--' * 40)
    IPs.append(Pad)
# Clear the IP address in case the next interface has a MAC but no IP address
    IP_Data = ''
    counter = counter + 1
d = int(len(IPs)/2)
print()
print(f'Number of Entries: {d}')
print()
print(f'Device Name: {device_name}')
print()
if my_json_file:
    print('Vlan   IP Address       MAC Address         Interface   Vendor')
    print('--' * 40)
else:
    print('Vlan   MAC Address         Interface   Vendor')
    print('--' * 30)
for IP in IPs:
    print(IP)

'''
hash the string of all macs. This gives a quick way to compare the
before and after MACS
'''

hash_list_str = str(hash_list)
# convert the string to bytes
b = hash_list_str.encode()
hash_object = hashlib.md5(b)
print()
print('Hash of all the MAC addresses')
print(hash_object.hexdigest())
print()

'''
print out the MAC Addresses sorted for review.
This is useful if the patch cables got mixed up during replacement
'''
print('Sorted list of MAC Addresses')
# print(hash_list)
for x in sorted(hash_list):
    print(x)
print('End of output')
