
#  Load modules
load_modules = {
    'gen_ping'  : {'bus': 'Default'},
    'mod_stat'    : {'debug': 2},
    'gen_replay'   : {'load_from': 'tests/test_responses.save', 'bus':'Default'}
}


# Scenario

actions = [
    {'gen_replay'     : {'pipe':1}},
    {'mod_stat':{'pipe': 1}},
    {'gen_ping'      : {
        'pipe':2,
        'range': [1790, 1810],
        'services':[
            {'service':0x01, 'sub':0x0d},
            {'service':0x09, 'sub':0x02},
            {'service':0x2F, 'sub':0x03,
             'data':[7,3,0,0]}],
        'mode':'UDS'}
    },
    {'mod_stat'   : {'pipe': 2}}

]