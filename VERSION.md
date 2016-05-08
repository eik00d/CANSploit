## Version 3.0-0
### CHANGES
 - hw_USBtin/engine lib mini feature: auto restart USBtin device if detected  overrun error. In this case all other modules will be stopped untill error will be fixed.
 - ecu_controls module added, noew you can configure ECU control and monitoring (regex now). Very useful as API 8)
 - cmd parametrisation changed a bit
 - mod_firewall can filter on BUS values!
 - by default all gen_* classes uses it's own BUS value (if not set then module name as BUS used)
 
## Version 2.8-0
### CHANGES
 - mod_stat feature: Print/Dump diff now have additional parameter - limit on uniq values. This will help a lot! Now you can do diff and exclude all 'noisy' frames
 
## Version 2.7-0
### CHANGES
 - mod_stat feature: search by ID 
 
## Version 2.6-0
### CHANGES
 - mod_stat refactoring: now we can support multi-biffers for sniffing and diff
 
## Version 2.5-0
### CHANGES
 - USBtin can be emulated/used via loop:// 
 - mod_stat UDS analyzer now supports PADDING in CAN Frames
 - UDS lib now support padding
 - EXPERIMENTAL: mod_stat can calculate needed delay for gen_ping/gen_replay/gen_fuzz modules

## Version 2.0-0
### CHANGES
 - Ported to Python 3.4 (Python 2.7 not supported)
 - hw_CANSocket added: support of linux CAN Socket
 - Anton's request: USBTin - change speed to local USBTin restart if USBtin was active
 
## Version 1.5-7
### CHANGES
 - mod_stat: support meta input ID as hex value
 - mod_stat: print values in hex
 - mod_replay: can read replay format where ID is hex
 
## Version 1.5-6
### CHANGES
 - gen_* modules: can work in serial mode - will inject frames in "free" holes in the main loop.
 
## Version 1.5-5
### CHANGES
 - mod_stat feature: description now not only by ID but by ASCII HEX regex!
 - mod_stat DIFF feature: now we can detect CAN frames by known amount of execution
 - mod_stat feature REMOVED: index-byte meta ... really do not see it useful for now

## Version 1.5-1
### CHANGES
 - hw_USBtin fix: direct name/path to serial port now should work
 - hw_CANBusTriple fix: when direct name/path to serial port used, do checking if device is there
 
## Version 1.5-0
### CHANGES
 - hw_USBtin fix - bug with writing 29bits ID... very bad bug. Sorry 8)

## Version 1.4-2
### CHANGES
 - mod_stat: added dump diff to replay format... 
 - fixed lib FRAG crash on 0 size frames...
 
## Version 1.4-1
### CHANGES
 - new web design/logo (thx my wife Sevtalana Sintcova!)

## Version 1.4-0
### CHANGES
 - mod_stat diff mode added: now we can compare "new" traffic and "old" to fins new ID/frames
 -- details: http://asintsov.blogspot.de/2016/04/cantoolz-modstat-diff-mode.html
 - now commands can be disabled (in Diff mod of mod_stat you can't use some commands)

## Version 1.3-3
### CHANGES
 - USBTin default bitrates calc added. Any speed/rate supported! (forgot that rate can be float... now it is fixed)
 
## Version 1.3-2
### CHANGES
 - USBTin default bitrates calc added. Any speed/rate supported!
 
## Version 1.3-1
### CHANGES
 - USBTin default bitrates added to the list 

## Version 1.3-0
### CHANGES
 - CAN module change: now we do not store additional raw data. We have saved up to 50% memory! But now "write" operation a little bit longer...
 - BUS name as any string now (except CBT, should be num 1, 2 or 3)
 - mod_ping/ gen_replay - delay added. This could be helpful when USBtin is overflowed with "write requests"
 - WEB API: Status bar added
 - FrontEnd status bar done
 
## Version 1.2-5
### CHANGES
 - FrontEnd fix: now parameters and options showing actual status (by Sergey Kononenko)
 
## Version 1.2-4
### CHANGES
 - libs/module.py workaround feature added: Now we can get current status of the module. This is needed because you need to know when ping/fuzz finished. Later we will think about proper status-bar 
 
## Version 1.2-3
### CHANGES
 - mod_stat design change: now Analysis function is parametrized, if you do not want to see all output
 - gen_ping fix: uds scan for non sub-commands fixed, new subbcomands added
 - example uds_scan changed

## Version 1.2-2
### CHANGES
 - WEB interface fix: dependences from Intrnet connection (d3 external web) 

## Version 1.2-1
### CHANGES
 - mod_stat fix: table print format 

## Version 1.2-0
### CHANGES
 - mod_stat feature added: ASCII detection (print ASCII if found in the traffic)
 - mod_stat feature added: Marking CAN frames via metafile/metadata (COMMENTS for ID)
 - mod_stat feature added: Marking control bytes via metafile/metada  to re-assemble fragmented frames 
 - mod_stat feature added: experimental chain detection (re-assemble fragmented frames that are sent in LOOP)
 - mod_stat fix: UDS/ISO tp detection bug fixed (when you scan more)
 - mod_stat change: now it stores ALL packets, not just table, and save in REPLAY save all these frames (WARNINING: Now  this module stores all frames, which can affect memory and speed. Let's see how it works...)
 - mod_stat feature removed: alert feature removed
 

## Version 1.1-1
### CHANGES
 - mod_stat fixes: better output, simple dump functions

## V1.1b
### CHANGES
 - Fixed mod_stat analysis option bug, when CAN Frame has 1 byte size
 - Default sniff config added


## V1.0b
### CHANGES
First Beta

