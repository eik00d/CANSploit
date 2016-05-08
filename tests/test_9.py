load_modules = {
    'hw_USBtin':    {'port':'loop', 'debug':2, 'speed':500},  # IO hardware module

    'ecu_controls':
        {'bus':'ECU_TEST',

        'commands':[
        {'cmd':'a','Unlock':'0x122:2:fff0'},
        {'Lock'  :'0x122:2:ffff'},
        {'Open Trunk':'290:2:ffa0'}
        ],

        'statuses':[

            {'cmd':'b','Door  - Rear passenger':{
                'Open':'0x133#ff.*',
                'Closed':'0x133#00.*'
            }},

            {'Door  - Front driver':{
                'Open':'0x133#..FF.*',
                'Closed':'0x133#..00.*'
            }}

        ]
    },
    'mod_firewall': {},
    'mod_stat':    {},
    'mod_stat~2':    {}
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},
    {'ecu_controls'     : {}},
    {'mod_stat':{}},
    {'mod_firewall': {'white_bus': ['ECU_TEST']}},
    {'mod_stat~2':{}},
    {'hw_USBtin':    {'action':'write','pipe': 2}}
    ]