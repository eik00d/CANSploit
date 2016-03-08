from libs.isotp import *

'''
UDS protocols support
'''


class UDSMessage:
    services_base = {
        0x01: [
            {None: 'Powertrain'},
            {0x0d: 'Req Current Powertrain'}
        ],
        0x03: [
            {None: 'Req Emission-Related Diag. Trb. Codes'}
        ],
        0x04: [
            {None: 'Clear/Reset Emsission Diag. Trb. Codes'}
        ],
        0x07: [
            {None: 'Req Emission-Related Diag. Trb. Codes during last cycle'}
        ],
        0x09: [
            {None: 'Vehicle info'},
            {0x02: 'Req Vehicle info (VIN)'},
            {0x04: 'Req ID'},
            {0x06: 'Veryf. num'},
            {0x0A: 'ECU name'},
            {0x0D: 'Vehicle info'}
        ],
        0x0A: [
            {None: 'Req Emission-Related Diag. Trb. Codes with perm status'}
        ],
        0x10: [
            {None: 'Diagnostic Session Control'},
            {0x03: 'Extended Diag Session'}
        ],
        0x11: [
            {None: 'Reset unknwn'},
            {0x01: 'ECU HARD Reset'},
            {0x03: 'Soft reset'},
            {0x02: 'ECU Reset'}],
        0x19: [
            {None: 'DTC unknws'},
            {0x01: 'Report num of DTC by status'},
            {0x02: 'Report DTC by status'},
            {0x03: 'Report DTC Snapshot ID'}
        ],
        0x27: [
            {None: 'Security Access'},
            {0x01: 'Seed request'},
            {0x02: 'Resposne', 'data': [0x01, 0x02, 0x03]}
        ],
        0x28: [{None: 'Communication Control'}],
        0x3E: [{None: 'Tester Present'}],
        0x83: [{None: 'Access Timing Parameters'}],
        0x84: [{None: 'Secured Data Transmission'}],
        0x85: [{None: 'Control DTC Settings'}],
        0x86: [{None: 'Response On Event'}],
        0x87: [{None: 'Link Control'}],
        0x22: [{None: 'Read Data By Identifier'}],
        0x23: [{None: 'Read Memory By Address'}],
        0x24: [{None: 'Read Scaling Data By Identifier'}],
        0x2A: [{None: 'Read Data By Identifier Periodic'}],
        0x2C: [{None: 'Dynamically Define Data Identifier'}],
        0x2E: [{None: 'Write Data By Identifier'}],
        0x3D: [{None: 'Write Memory By Address'}],
        0x14: [{None: 'Clear Diagnostic Information'}],
        0x2F: [{None: 'Input Output Control By Identifier'}],
        0x31: [{None: 'Routine Control'}],
        0x34: [{None: 'Request Download'}],
        0x35: [{None: 'Request Upload'}],
        0x36: [{None: 'Transfer Data'}],
        0x37: [{None: 'Request Transfer Exit'}],
        0x38: [{None: 'Request File Transfer'}]
    }

    error_responses = {
        0x10: 'General reject',
        0x11: 'Service not supported',
        0x12: 'Subfunction not supported',
        0x13: 'Incorrect message length or invalid format',
        0x14: 'Response too long',
        0x21: 'Busy repeat request',
        0x22: 'Condition not correct',
        0x24: 'Request sequence error',
        0x25: 'No response from subnet component',
        0x26: 'Failure prevents execution of requested action',
        0x31: 'Request out of range',
        0x33: 'Security access denied',
        0x35: 'Invalid key',
        0x36: 'Exceeded number of attempts',
        0x37: 'Required time delay not expired',
        0x39: 'Reserved by extended data link security document',
        0x3A: 'Reserved by extended data link security document',
        0x3B: 'Reserved by extended data link security document',
        0x3C: 'Reserved by extended data link security document',
        0x3D: 'Reserved by extended data link security document',
        0x3E: 'Reserved by extended data link security document',
        0x3F: 'Reserved by extended data link security document',
        0x40: 'Reserved by extended data link security document',
        0x41: 'Reserved by extended data link security document',
        0x42: 'Reserved by extended data link security document',
        0x43: 'Reserved by extended data link security document',
        0x44: 'Reserved by extended data link security document',
        0x45: 'Reserved by extended data link security document',
        0x46: 'Reserved by extended data link security document',
        0x47: 'Reserved by extended data link security document',
        0x48: 'Reserved by extended data link security document',
        0x49: 'Reserved by extended data link security document',
        0x4A: 'Reserved by extended data link security document',
        0x4B: 'Reserved by extended data link security document',
        0x4C: 'Reserved by extended data link security document',
        0x4D: 'Reserved by extended data link security document',
        0x4E: 'Reserved by extended data link security document',
        0x4F: 'Reserved by extended data link security document',
        0x70: 'Upload/download not accepted',
        0x71: 'Transfer data suspended',
        0x72: 'General programming failure',
        0x73: 'Wrong block sequence counter',
        0x78: 'Request correctly received but response is pending',
        0x7E: 'Subfunction not supported in active session',
        0x7F: 'Service not supported in active session'
    }

    def __init__(self, _shift = 0x08):  # Init Session
        self.sessions = {}
        self.shift = _shift

    def start_session(self, _id):
        if _id in self.sessions:
            return -1
        else:
            self.sessions[_id] = {}
            return 1

    def delete_session(self, _id):
        if _id not in self.sessions:
            return -1
        else:
            del self.sessions[_id]
            return 1

    def check_status(self, _input_message):
        if _input_message.message_id in self.sessions:
            if _input_message.message_data[0] in self.sessions[_input_message.message_id]:
                return 1
            else:
                return -1
        elif (_input_message.message_id - self.shift) in self.sessions:
            if (_input_message.message_data[0] - 0x40) in self.sessions[_input_message.message_id - self.shift]:
                return 2
            else:
                return -2
        else:
            return 0

    # Method to handle messages ISO TP messages
    def handle_message(self, _input_message):
        if self.check_status(_input_message) == 1:
            return False
        elif self.check_status(_input_message) == 2: # Possible response came
            sts = self.sessions[_input_message.message_id - self.shift][_input_message.message_data[0]-0x40]['status']
            if sts == 0:  # Ok, now we have Response... looks like
                return self.add_raw_response(_input_message)
            return False
        elif self.check_status(_input_message) == -1:  # New service request
            self.add_raw_request(_input_message)
            return True
        elif self.check_status(_input_message) == -2: # Maybe error
            return self.add_raw_response(_input_message)
        else:                                         # New Service request and new ID
            self.add_raw_request(_input_message)
            return True
        return False

    def add_request(self, _id, _service, _subcommand = 0, _data = []):
        if _id not in self.sessions:
            self.start_session(_id)

            self.sessions[_id][_service] = {
                'sub': _subcommand,
                'data': _data,
                'response': {
                    'id': None, 'sub': None, 'data': None, 'error': None
                },
                'status': 0
            }

            byte_data = [_service, _subcommand] + _data
            return ISOTPMessage.generate_can(_id, byte_data)

    def add_raw_request(self, _input_message):
        if _input_message.message_id not in self.sessions:
            self.start_session(_input_message.message_id)

        self.sessions[_input_message.message_id][_input_message.message_data[0]] = {
                'sub': _input_message.message_data[1],
                'data': _input_message.message_data[2:],
                'response': {
                    'id': None, 'sub': None, 'data': None, 'error': None
                },
                'status': 0
            }
        return True

    def add_raw_response(self, _input_message):
        if (_input_message.message_id - self.shift) in self.sessions:
            if (_input_message.message_data[0] - 0x40) in self.sessions[(_input_message.message_id - self.shift)]:
                self.sessions[(_input_message.message_id - self.shift)][_input_message.message_data[0] - 0x40]['response']['id'] = _input_message.message_id
                self.sessions[(_input_message.message_id - self.shift)][_input_message.message_data[0] - 0x40]['response']['sub'] = _input_message.message_data[1]
                self.sessions[(_input_message.message_id - self.shift)][_input_message.message_data[0] - 0x40]['response']['data'] = _input_message.message_data[2:]
                self.sessions[(_input_message.message_id - self.shift)][_input_message.message_data[0] - 0x40]['status'] = 1
                return True
            elif _input_message.message_data[0] in self.error_responses:
                x = self.sessions[(_input_message.message_id - self.shift)].keys()[-1]
                self.sessions[(_input_message.message_id - self.shift)][x]['response']['id'] = _input_message.message_id
                self.sessions[(_input_message.message_id - self.shift)][x]['response']['sub'] = None
                self.sessions[(_input_message.message_id - self.shift)][x]['response']['data'] = None
                self.sessions[(_input_message.message_id - self.shift)][x]['status'] = 2
                self.sessions[(_input_message.message_id - self.shift)][x]['response']['error'] = self.error_responses[_input_message.message_data[0]]
                return True
        return False

    def get_last_response(self, _id, _service):
        if _id in self.sessions and _service in self.sessions[_id]:
            return self.sessions[_id][_service]['response']
        return {}
