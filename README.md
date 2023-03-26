[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![GitHub language count](https://img.shields.io/github/languages/count/rikosintie/nmap-python)
![Twitter Follow](https://img.shields.io/twitter/follow/rikosintie?style=social)

# MAC2Manuf
Convert the output from "show mac add int g1/0/1 | i Gi" to the manufacturer name.

The script uses Michael Huang's manuf python library at [Parser library for Wireshark's OUI database.](https://github.com/coolbho3k/manuf)

Requires Python 3.x, json library, hashlib, icecream library

To install the libraries:

```
python -m pip install json
python -m pip install hashlib
```

The icecream library is used for debugging. 

To install icecream run the following:  
`python -m pip install icecream`

If you don't plan to modify the script you can just delete:
```
from icecream import ic
# ic.enable()
ic.disable()
```
and any line that starts with `ic()`.

If you do any python programming I recommend that you look at the icecream library for debugging.  
[icecream on github.com](https://github.com/gruns/icecream)

## What would I use the script for?
Useful when you are looking for a specific brand device and have a lot of ports to review. It is also useful when replacing a switch. Run it before the cutover and save the results, then run it after the cutover and use [Meld](meldmerge.org) or your favorite comparison tool to make sure all MACs are in the correct port.

The included spreadsheet has the show commands for Gigabit, FastEthernet, the old 3550 and a FEX switch pre-built.

NOTE: To download the spreadsheet, click on it and then select Download. Do not right click and select "Save Link As...".

The output will look similar to this:
```
test-switch#show mac add int g1/0/1 | i Gi
  10    8434.97a7.708b    DYNAMIC     Gi1/0/1
test-switch#show mac add int g1/0/2 | i Gi
test-switch#show mac add int g1/0/3 | i Gi
  10    0c4d.e9c1.4a0d    DYNAMIC     Gi1/0/3
test-switch#show mac add int g1/0/4 | i Gi
test-switch#show mac add int g1/0/5 | i Gi
  10    0c4d.e9c1.363c    DYNAMIC     Gi1/0/5
```
Simply paste the appropriate spreadsheet data into the switch and save the output in a text file with the name "mac-addr.txt".

The Python script will clean up the output and look up the manufacture in the Wireshark OUI database.

`python3 macaddr.py`

The output will look simiiar to this:
```
Number Entries: 53 

Vlan   MAC Address      Type       Interface   Vendor
------------------------------------------------------------
45     2c59.e57b.ce46   DYNAMIC    Gi1/0/16    HewlettP
------------------------------------------------------------
45     2c59.e5d4.c1f9   DYNAMIC    Gi1/0/43    HewlettP
------------------------------------------------------------
45     001e.0b08.81bc   DYNAMIC    Gi1/0/47    HewlettP
------------------------------------------------------------
45     38ea.a709.cbbf   DYNAMIC    Gi2/0/18    HewlettP
------------------------------------------------------------
45     509a.4c3e.61eb   DYNAMIC    Gi2/0/44    Dell
------------------------------------------------------------
45     0026.735a.00c8   DYNAMIC    Gi4/0/13    Ricoh
```
**Add the IP address**

You can use the python script [arp.py](https://github.com/rikosintie/ARP-Sort) to convert the output of `show ip arp` on a core switch to MAC addresses/IP Addresses. It also creates a JSON file that macaddr.py can read. If you create the json file before running macaddr.py you will get output that looks like this:
```
Number Entries: 53 

Vlan   MAC Address      Type       Interface   IP               Vendor
--------------------------------------------------------------------------------
45     2c59.e57b.ce46   DYNAMIC    Gi1/0/16    125.180.245.28   HewlettP
--------------------------------------------------------------------------------
45     2c59.e5d4.c1f9   DYNAMIC    Gi1/0/43    125.180.245.31   HewlettP
--------------------------------------------------------------------------------
45     001e.0b08.81bc   DYNAMIC    Gi1/0/47    125.180.245.45   HewlettP
--------------------------------------------------------------------------------
45     38ea.a709.cbbf   DYNAMIC    Gi2/0/18    125.180.245.22   HewlettP
--------------------------------------------------------------------------------
45     509a.4c3e.61eb   DYNAMIC    Gi2/0/44    125.180.245.40   Dell
--------------------------------------------------------------------------------
45     0026.735a.00c8   DYNAMIC    Gi4/0/13    125.180.245.90   Ricoh
--------------------------------------------------------------------------------
45     6416.7f93.892a   DYNAMIC    Gi4/0/15    125.180.252.39   Polycom

```
**Using PingInfoView**

[PingInfoView](https://www.nirsoft.net/utils/multiple_ping_tool.html) is a great free tool from Nirsoft that takes a text file with IP addresses and hostnames and then continuously pings them. It's perfect for making sure all devices are back online after you replace a switch.

Here is output from the script. Obviously, we don't get the hostname from the switch so I use the MAC Address. When PingInfoView is running it will resolve the hostname from DNS if possible.
```
PingInfo Data
10.56.238.150 b499.ba01.bc82
10.56.239.240 0026.5535.7b7a
```

![PingInfoView Sample](https://github.com/rikosintie/MAC2Manuf/blob/master/PingInfoView.PNG "PingInfoView Sample")


**A Hash of the MACs**

I recently was involved with a switch replacement where the first thirty ports were just edge ports for PCs and phones but the last 18 ports had VMware ESXi, alarms, etc. The cables for the first thirty ports didn't get patched back in the same order that they were originally. Re-running the script after the replacement didn't help verify that everything was back because they were in differnet ports.

I added two outputs to help in this situation. The first is an MD5 hash of the MACs. The script sorts them first so the order on the switch doesn't matter. As a quick check you can just compare the hash before and after.

The second is the sorted output of the MACs. If the hashes don't match, just throw the before and after output into Meld or notepad++ and you will instantly see what is missing. In my case it was three virtual servers off the ESXi host so it was nice to see it quickly and be able to correct it.

Output

```
Hash of all the MAC addresses
e414668f2c6214a2fd6f25df7b897eda

Sorted list of MAC Addresses
000e.7fb4.1919
0011.85b8.bf8d
0025.b323.f8cc
```
Here is a terminal recoding of the script in action [python3 macaddr.py](https://asciinema.org/a/570215)

asciicinema is a cool little python script for recording terminal sessions. It can be found on github.com here:
[asciicinema](https://github.com/asciinema/asciinema)

