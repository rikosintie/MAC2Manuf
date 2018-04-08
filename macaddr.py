'''
References:
https://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python/6545090#6545090
https://stackoverflow.com/questions/20944483/python-3-sort-a-dict-by-its-values
https://docs.python.org/3.3/tutorial/datastructures.html
https://www.quora.com/How-do-I-write-a-dictionary-to-a-file-in-Python
https://www.programiz.com/python-programming/break-continue

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

Uses the Parser library for Wireshark's OUI database from https://github.com/coolbho3k/manuf to convert the MAC to a manufacture.
The database needs to be updated occaisionally using: 

python3 manuf.py -u


Changelog
March 7, 2018
Added code to read Mac2IP.json and save it as a dictionary.
Mac2IP.json is created by running arp.py against the output "show ip arp" or "sh ip arp vlan x" on a core switch
if Mac2IP.json is found in the same directory as macaddr.py it adds the IP address to the output.
if Mac2IP.json is not found the IP address is not added
Vlan     MAC Address      Interface      IP           Vendor
   20    f8b1.56d2.3c13     Gi1/0/3   10.129.20.70    Dell
 ----------------------------------------------------------------
   20    0011.431b.b291     Gi1/0/16   10.129.20.174    Dell
 ----------------------------------------------------------------

March 24, 2018
Added an MD5 hash function to the list of MAC addresses. This gives a quick comparison of the before
and after is some cables got swapped but are on the correct vlan.
Added a sorted output of the MAC addresses. If there are differences before and after you 
can save the list of MACs and use MELD or Notepad++ (with the compare plugin) to see what is different.
 
Hash of all the MAC addresses
6449620420f0d67bffd26b65e9a824a4

Sorted list of MAC Addresses
0018.c840.1295
0018.c840.12a8
0027.0dbd.9f6e

 April 7, 2018
Added output for PingInforview (nirsoft.net)

PingInfo Data
10.56.238.150 b499.ba01.bc82
10.56.239.240 0026.5535.7b7a

'''

import manuf
import sys
import json
import hashlib

vernum = '1.1'
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
#create an empty list to hold MAC addresses for hashing
hash_list = []
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
#10.56.254.2     00:04:44  c08c.6036.19ef  Vlan254
    for line in f:
#strip out lines without DYNAMIC or dynamic 
        if line.find('.') != -1 or line.find('dynamic') != -1:
            data.append(line)
    f.close
ct = len(data)-1
counter = 0
IPs = []
print('PingInfo Data')
while counter <= ct:
    IP = data[counter]
#Remove Enter
    IP = IP.strip('\n')
    IP = IP.upper()
#extract MAC Address and save to hash_list for hashing
#   2    6cb2.ae09.f8c4    DYNAMIC     Gi2/0/2
    L = str.split(IP)
    Mac = L[1]
    Mac = Mac.lower()
    temp = hash_list.append(Mac)
    if Mac in Mac_IP:
        IP_Data = Mac_IP[Mac]
#       print the pinginfo data
        print(IP_Data, Mac)
#pull the manufacturer with manuf
    manufacture = p.get_manuf(Mac)
#strip out the word DYNAMIC
    IP = IP.replace('DYNAMIC    ','')
#the 6800 series adds an * to the beginning of the line.
#*     239 685b.35c3.4e7a  DYNAMIC  Yes        0     Gi101/1/0/47
    IP = IP.replace('*     ','')
#Build the string
    IP = IP + "   "  + IP_Data + "    " + str(manufacture)
    IPs.append(str(IP))
    IPs.append('--------------------------------------------------------------------')
#    IPs.append('****************************************************************************')
    counter = counter + 1
d = int(len(IPs)/2) 
print()
print ('Number Entries: %s ' %d)
print()
if mydatafile:
    print('Vlan     MAC Address      Interface      IP           Vendor')
else:
    print('Vlan     MAC Address      Interface      Vendor')
for IP in IPs:
    print(IP)

'''
hash the string of all macs. This gives a quick way to compare the before
and after MACS
'''

hash_list_str = str(hash_list)
#convert the string to bytes
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
#print(hash_list)
for x in sorted(hash_list):
    print(x)
print('End of output')
