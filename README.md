# CANToolz
###aka YACHT (Yet Another Car Hacking Tool)
CANToolz is a framework for analysing CAN networks and devices.
This tool based on different modules which can be assembled in pipe together and
can be used by security researchers and automotive/OEM security testers for black-box analysis and etc. 
You can use this software for ECU discovery, MITM testing, fuzzing, bruteforcing, scanning or R&D testing and validation

This platform is a try to unify all needed tricks/tools and other things that you can do with CAN bus in one place.
I have found, that there are many tools available, from Charlie Miller and Chris Valasek tools to UDS/CAN tools by Craig Smith.
They all cool and useful, but it is still difficult to use it in every-day work (al least for me) and you need to modify/code 
a lot of thing to get something you want (MITM, scanners with some logic). That's why I have this software. If more people can 
contribute into modules, than more useful this thing can be. It gives (almost) an easy way to add your modules and use "extended" version for your needs
(like custom brutforcers for chosen ECU and etc). Just for fun... finally. No Forbs, Wires  or other big noise needed around this. 
Just want to have a good tool and people around.

Another thing: this is module based engine, so you can use it as part of your testing processes or include into more difficult scenarios/software where you need to work with CAN bus.

"I don't get why everyone releases new "car hacking tools" all the time.  @nudehaberdasher and I released ours in 2013 and they work fine." (c) Charlie Miller (‏@0xcharlie)

"Looking for our car hacking tools / data / scripts? http://illmatics.com/content.zip " (c) Chris Valasek ‏@nudehaberdasher

More details and use-case published in the [blog](http://asintsov.blogspot.de/)
See wiki (currently in dev.): [WIKI](https://github.com/eik00d/CANToolz/wiki)

## Using a Hardware

CANToolz can work with CAN network by using next hardware:

1. [USBtin](http://www.fischl.de/usbtin/)
2. [CANBus Triple](https://canb.us/)

### Fast start
sudo python cantoolz.py -g w -c examples/can_sniff.py 

Then use browser and connect to http://localhost:4444
  
## Modules

- hw_CANBusTriple  - IO module for CANBus Triple HW
- hw_USBtin        - IO module forUSBtin
- mod_firewall     - module for blocking CAN message by ID
- mod_fuzz1        - Simple 'Proxy' fuzzer  (1 byte) Can be combined with gen_ping/gen_replay
- mod_printMessage - printing CAN messages
- mod_stat         - CAN messages statistic (with .csv file output)
                     Analysis option (c mod_stat a) will try to find UDS/ISO TP messages
- gen_ping         - generating CAN messages with chosen IDs (ECU/Service discovery)
- gen_replay       - save and replay packets

P.S. of course we are working on supporting other types of I/O hardware and modules. Please join us!
Main idea that community can produce different modules that can be useful for all of us 8)

Sniffing and UDS detection example, screenshot:
![](https://1.bp.blogspot.com/-_SHafeN7ku0/Vyp4K_Lf_sI/AAAAAAAAAQ4/bVoDm-oN7C4v9t5fg0laAMqxQkEKfwUhQCLcB/s1600/vw2.png)

## Dependencies
    python 3.4
    pip install pyserial

Last stable release for Python 2.7: [https://github.com/eik00d/CANToolz/tree/Python_2.7_last_release](https://github.com/eik00d/CANToolz/tree/Python_2.7_last_release)

# Usage Examples
See more use-cases inside examples folder:

- CAN Switch filter scanner
    Checking which CAN frames can be passed from diagnostic interface to HU and back
- MITM with firewall (ECU ID detection)
    Checking what packets are responsible for chosen "action"
- Replay discovery
    Checking what packets are responsible for chosen "action"
- Ping discovery ( with ISO TP and UDS support)
    UDS detection and etc

And many other options possible. Just use modules as "needed".
[Example](https://asintsov.blogspot.de/2016/04/cantoolz-modstat-diff-mode.html) with DIFF mode, to find door unlock commands.

P.S.
 Current version is uber-beta. Not tested enough, code is not clean and ugly and there are bugs that not found yet... working on that, sorry.
 A lot of not-needed IF, and bad code, strange RPINTs and etc...
 Feel free to fix or ignore ;)

With best regards:

Alexey Sintsov   (@asintsov)
alex.sintsov@gmail.com

[DC#7812: DEFCON-RUSSIA](http://defcon-russia.ru)



