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

and create a list of Vlan, Mac Address and interface.


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


'''
#from socket import inet_aton
#import struct
#from socket import inet_aton,inet_ntoa
import manuf

# def ip2long(ip):
#     packed = inet_aton(ip)
#     lng = struct.unpack("!L", packed)[0]
#     return lng


# def long2ip(lng):
#     packed = struct.pack("!L", lng)
#     ip=inet_ntoa(packed)
#     return ip

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
#data2 = {}
while counter <= i:
    IP = listname[counter]
    #Remove Enter
    IP = IP.strip('\n')
    if IP.find('show') != -1:
        counter = counter + 1
        continue
#extract MAC Address
#   2    6cb2.ae09.f8c4    DYNAMIC     Gi2/0/2
    Mac = IP
#    MacAndVlan = IP
    Dot = Mac.find('.')
    Mac = Mac[Dot-4:Dot+10].rstrip('')
#    print(Mac)
    manufacture = p.get_all(Mac)
 #   MacAndVlan = MacAndVlan[38:70].rstrip('')
 #   MacAndVlan = MacAndVlan.replace('ARPA   Vlan','')
    

    IP = IP.replace('DYNAMIC    ','')
    IP = IP + "   " + str(manufacture)
    IPs.append(str(IP))
    IPs.append('****************************************************************************')
    counter = counter + 1
d = int(len(IPs)/2) 
print (' # Entries: %s ' %d)
print('Vlan     MAC Address      Interface')
#find the manufacturer from the mac address


for IP in IPs:
    print(IP)
