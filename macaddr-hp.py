'''
References:
https://github.com/wireshark/wireshark/blob/master/manuf
https://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python/6545090#6545090
https://stackoverflow.com/questions/20944483/python-3-sort-a-dict-by-its-values
https://docs.python.org/3.3/tutorial/datastructures.html
https://www.quora.com/How-do-I-write-a-dictionary-to-a-file-in-Python
https://www.programiz.com/python-programming/break-continue
https://www.ascii-art-generator.org/
#https://docs.python.org/3/howto/argparse.html
#https://pymotw.com/2/argparse/

read mac-addr.txt containing the output of
sh mac-address 11
sh mac-address 12
sh mac-address 13
sh mac-address 14

and create a list of Vlan, Mac Address, interface and manufacturer.

Number of Entries: 4

Vlan   MAC Address       Interface   Vendor
--------------------------------------------------
  24   3417eb-ba532f         11      Dell
--------------------------------------------------
 202   b4a95a-ab7608         11      Avaya
--------------------------------------------------
 202   38bb3c-bc311f         13      Avaya
--------------------------------------------------
  24   a4251b-30e9a8         14      Avaya
--------------------------------------------------


Uses the Parser library for Wireshark's OUI database from
https://github.com/coolbho3k/manuf to convert the MAC to a manufacture.
The database needs to be updated occaisionally using:

python3 manuf.py -u


Changelog
March 7, 2018
Added code to read Mac2IP.json and use it as a dictionary of IP to MAC.
Mac2IP.json is created by running arp-hp.py against the output
"show arp" on a core switch
if Mac2IP.json is found in the same directory as macaddr.py it adds the
IP address to the output.
if Mac2IP.json is not found the IP address is not added


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

May 15, 2018
Fixed a bug in the IP address selection loop. I wasn't clearing IP_Data at the
end of the loop so is an interface didn't have an IP address in the json file
it would use the last IP address.

Clear the IP address in case the next interface has a MAC but no IP address
    IP_Data = ''
'''

import argparse
import hashlib
import json
import re
import sys

import manuf

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=False, help="File to read from")
#   parser.add_argument('-o', '--output', type=str, help="Output file.")
args = parser.parse_args()


vernum = '1.0'
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
    print("+----------------------------------------------------------------------+")
    print("| "+ sys.argv[0] + " Version "+ vernum +"                                               |")
    print("| This program is free software; you can redistribute it and/or modify |")
    print("| it in any way you want. If you improve it please send me a copy at   |")
    print("| the email address below.                                             |")
    print("|                                                                      |")
    print("| Author: Michael Hubbard, michael.hubbard999@gmail.com                |")
    print("|         mwhubbard.blogspot.com                                       |")
    print("|         @rikosintie                                                  |")
    print("+----------------------------------------------------------------------+")


version()
# MAC addresses are expressed differently depending on the manufacture and even model device
# the formats that this script can parse are:
# 0a:0a:0a:0a:0a:0a, 0a-0a-0a-0a-0a-0a, 0a0a0a.0a0a0a0 and 0a0a0a-0a0a0a
# this should cover most Cisco and HP devices.
#
print()
# create an empty dictionary to hold the mac-IP data
Mac_IP = {}
IP_Data = ''
device_name = 'Not Found'
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
# args.file contains the string entered after -f. That's becuase of the --file in the parser.add_argument function.
if args.file:
    mydatafile = args.file
else:
    mydatafile = 'mac-addr.txt'
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
        match_Interface = line.find('Port Address Table')
        if match_PC or match_Cisco or match_HP or match_Interface != -1:
            data.append(line)
        device_name_loc = line.find('#')
        if device_name_loc != -1:
            device_name = line[0:device_name_loc]
            device_name = device_name.strip()
    f.close
ct = len(data)-1
counter = 0
IPs = []
print()
print('Device Name: %s ' % device_name)
print('PingInfo Data')
while counter <= ct:
    IP = data[counter]
# Remove newline at end
    IP = IP.strip('\n')
#If the line contains Port Address Table
#    if line.find('Port Address Table'):
    if IP.find('Port Address Table') != -1:
#   Remove the Status and Counters text.
        IP = IP.replace('Status and Counters - ','')
        L = str.split(IP)
        Interface_Num = L[4]
        Vlan = ''
        IP_Data = ''
        Mac = ''
        manufacture = ''
    else:
        L = str.split(IP)
        Mac = L[0]
        Vlan = L[1]
        Vlan = Vlan.replace(',...','')
        temp = hash_list.append(Mac)
        if Mac in Mac_IP:
            IP_Data = Mac_IP[Mac]
        else:
            IP_Data = 'No-Match'
# print the pinginfo data
        print(IP_Data, Mac)
# pull the manufacturer with manuf
        manufacture = p.get_manuf(Mac)
# Pad with spaces for output alignment
        Front_Pad = 4 - len(Vlan)
        Pad = 7 - len(Vlan) - Front_Pad
        Vlan = (' ' * Front_Pad) + Vlan + (' ' * Pad)
# Pad MAC Address Field
        Pad = 22 - len(Mac)
        Mac = Mac + (' ' * Pad)
# Pad Interface
        Pad = 8 - len(Interface_Num)
        Interface_Num = Interface_Num + (' ' * Pad)
# Pad IP address field if the json file exists
    if my_json_file:
        Pad = 17 - len(IP_Data)
        IP_Data = IP_Data + (' ' * Pad)
# create the separator at 80 characters
        Pad = '--' * 35
    else:
# if not create the separator at 60 characters since there won't be IPs
        Pad = '--' * 25
        IP_Data = ''
# Build the string
    if IP.find('Port Address Table') != -1:
        counter = counter + 1
        continue
    else:
        IP = Vlan + IP_Data + Mac + Interface_Num + str(manufacture)
        IPs.append(str(IP))
        IPs.append(Pad)
# Clear the IP address in case the next interface has a MAC but no IP address
    IP_Data = ''
    counter = counter + 1
d = int(len(IPs)/2)
print()
print('Number of Entries: %s ' % d)
print()
print('Device Name: %s ' % device_name)
if my_json_file:
    print('Vlan   IP Address       MAC Address       Interface   Vendor')
    print('--' * 35)
else:
    print('Vlan   MAC Address       Interface   Vendor')
    print('--' * 25)
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
