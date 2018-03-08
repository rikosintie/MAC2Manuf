'''
References:
https://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python/6545090#6545090
https://stackoverflow.com/questions/20944483/python-3-sort-a-dict-by-its-values
https://docs.python.org/3.3/tutorial/datastructures.html
https://www.quora.com/How-do-I-write-a-dictionary-to-a-file-in-Python

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
  10    8434.97a7.708b     Gi1/0/1   Vendor(manuf='HewlettP', comment=None)
****************************************************************************
  10    0c4d.e9c1.4a0d     Gi1/0/3   Vendor(manuf='Apple', comment=None)
****************************************************************************

Uses the Parser library for Wireshark's OUI database from https://github.com/coolbho3k/manuf to convert the MAC to a manufacture.
The database needs to be updated occaisionally using: 

python3 manuf.py -u

'''
# Changelog
# March 7, 2018
# Added code to read Mac2IP.json and save it as a dictionary.
# Mac2IP.json is created by running arp.py against the output "show ip arp" or "sh ip arp vlan x" on a core switch
# if Mac2IP.json is found in the same directory as macaddr.py it adds the IP address to the output.
# if Mac2IP.json is not found the IP address is not added
# Vlan     MAC Address      Interface      IP           Vendor
#   20    f8b1.56d2.3c13     Gi1/0/3   10.129.20.70    Vendor(manuf='Dell', comment=None)
# ****************************************************************************
#   20    0011.431b.b291     Gi1/0/16   10.129.20.174    Vendor(manuf='Dell', comment=None)
# ****************************************************************************

import manuf
import sys
import json

vernum = '1.0'
def version():
    """
    This function prints the version of this program. It doesn't allow any argument.
    """
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

#create a space between the command line and the output
print()
#create an empty dictionary to hold the mac-IP data
Mac_IP = {}
IP_Data = ''
#Open the json created by arp.py if it exists
mydatafile = 'Mac2IP.json'
try:
    with open(mydatafile) as f:
        Mac_IP = json.load(f)
except FileNotFoundError: 
    print(mydatafile + ' does not exist')
    mydatafile = None

p = manuf.MacParser()
#create a blank list to accept each line in the file
data = []
try:
    f = open('mac-addr.txt', 'r')
except FileNotFoundError:
            print('mac-addr.txt does not exist')
else:    
    for line in f:
#strip out empty lines
        if line.find('DYNAMIC'):
            data.append(line)
    f.close
ct = len(data)-1
counter = 0
IPs = []
while counter <= ct:
    IP = data[counter]
#Remove Enter
    IP = IP.strip('\n')
#skip any line with the command
    #if IP.find('show') != -1:
    if IP.find('DYNAMIC') == -1:
        counter = counter + 1
        continue
#extract MAC Address
#   2    6cb2.ae09.f8c4    DYNAMIC     Gi2/0/2
    L = str.split(IP)
    Mac = L[1]
#    print(Mac)
    if Mac in Mac_IP:
        IP_Data = Mac_IP[Mac]

#pull the manufacturer with manuf
    manufacture = p.get_all(Mac)
#strip out the word DYNAMIC
    IP = IP.replace('DYNAMIC    ','')
#Build the string
    IP = IP + "   "  + IP_Data + "    " + str(manufacture)
    IPs.append(str(IP))
    IPs.append('****************************************************************************')
    counter = counter + 1
d = int(len(IPs)/2) 
print ('Number Entries: %s ' %d)
print()
if mydatafile:
    print('Vlan     MAC Address      Interface      IP           Vendor')
else:
    print('Vlan     MAC Address      Interface      Vendor')
for IP in IPs:
    print(IP)
