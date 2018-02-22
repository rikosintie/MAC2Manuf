# MAC2Manuf
Convert the output from "show mac add int g1/0/1 | i Gi" to the manufacturer name.

Requires Wireshark, because it uses Michael Huang's manuf python library at [Parser library for Wireshark's OUI database.](https://github.com/coolbho3k/manuf)
Requires Python 3.x

Useful when you are looking for a specific brand device and have a lot of ports to review. I think this would also be useful when replacing a switch. Run it before the cutover and save the results, then run it after the cutover and use [Meld](meldmerge.org) or your favorite comparison tool to make sure all MACs are in the correct port.

The included spreadsheet has the show commands for Gigabit, FastEthernet, the old 3550 and a FEX switch pre-built.

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
Entries: 65 
Vlan     MAC Address      Interface
  10    8434.97a7.708b     Gi1/0/1   Vendor(manuf='HewlettP', comment=None)
****************************************************************************
  10    0c4d.e9c1.4a0d     Gi1/0/3   Vendor(manuf='Apple', comment=None)
****************************************************************************
  10    0c4d.e9c1.363c     Gi1/0/5   Vendor(manuf='Apple', comment=None)
****************************************************************************
```

