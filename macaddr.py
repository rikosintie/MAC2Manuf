'''
References:
https://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python/6545090#6545090
https://stackoverflow.com/questions/20944483/python-3-sort-a-dict-by-its-values
https://docs.python.org/3.3/tutorial/datastructures.html

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
# Entries: 65 
Vlan     MAC Address      Interface
  10    8434.97a7.708b     Gi1/0/1
**************************************
  10    0c4d.e9c1.4a0d     Gi1/0/3
**************************************

Uses the Parser library for Wireshark's OUI database from https://github.com/coolbho3k/manuf to convert the MAC to a manufacture.
The database needs to be updated occaisionally using: 

python3 manuf.py -u

'''
#from socket import inet_aton
#import struct
#from socket import inet_aton,inet_ntoa
import manuf

#create a space between the command line and the output
print()
p = manuf.MacParser()
#create a blank list to accept each line in the file
listname = []
f = open('mac-addr.txt', 'r')
for line in f:
    listname.append(line)
f.close
# string length
i = len(listname)-1
#d = i + 1
counter = 0
IPs = []
data = {}
while counter <= i:
    IP = listname[counter]
#Remove Enter
    IP = IP.strip('\n')
#skip any line with the command
    if IP.find('show') != -1:
        counter = counter + 1
        continue
#extract MAC Address
#   2    6cb2.ae09.f8c4    DYNAMIC     Gi2/0/2
    Mac = IP
    Dot = Mac.find('.')
    Mac = Mac[Dot-4:Dot+10].rstrip('')
#pull the manufacturer with manuf
    manufacture = p.get_all(Mac)
#strip out the word DYNAMIC
    IP = IP.replace('DYNAMIC    ','')
#Build the string
    IP = IP + "   " + str(manufacture)
    IPs.append(str(IP))
    IPs.append('****************************************************************************')
    counter = counter + 1
d = int(len(IPs)/2) 
print ('Number Entries: %s ' %d)
print()
print('Vlan     MAC Address      Interface')

for IP in IPs:
    print(IP)
