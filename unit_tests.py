import sys
import unittest
import time
import codecs

class EcuControl(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay_padding(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_9.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "x")
        ret2 = self.CANEngine.call_module(1, "b")
        self.assertTrue(ret.find("Unknown") > 0, "Nothing yet")
        self.assertTrue(ret2.find("Unknown") > 0, "Nothing yet")

        self.CANEngine.call_module(0,"t t13320000")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "x")
        ret2 = self.CANEngine.call_module(1, "b")
        print(ret)
        self.assertFalse(ret.find("Unknown") > 0, "Should be status")
        self.assertFalse(ret2.find("Unknown")> 0, "Should be statu")
        self.assertTrue(ret.find("Closed") > 0, "Should be status")
        self.assertTrue(ret2.find("Closed") > 0, "Should be statu")

        self.CANEngine.call_module(0,"t t1332ff22")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "x")
        ret2 = self.CANEngine.call_module(1, "b")
        self.assertTrue(ret.find("Closed") > 0, "Should be status")
        self.assertTrue(ret2.find("Open") > 0, "Should be status")

        self.CANEngine.call_module(1, "z")
        self.CANEngine.call_module(1, "a")
        time.sleep(1)
        ret = self.CANEngine.call_module(2, "p")
        ret2 = self.CANEngine.call_module(4, "p")

        self.assertTrue(ret.find("0x122") > 0, "0x122 should be there")
        self.assertTrue(ret.find("fff0") > 0, "fff0 as body should be there")
        self.assertTrue(ret.find("ffff") > 0, "ffff as body should be there")
        self.assertTrue(ret.find("ff22") > 0, "ffff as body should be there")
        self.assertTrue(ret.find("0x133") > 0, "0x133 should be there")
        self.assertFalse(ret2.find("0x133") > 0, "0x133 should NOT be there")
        self.assertFalse(ret2.find("ff22") > 0, "0x133 should NOT be there")
        self.assertTrue(ret2.find("0x122") > 0, "0x122 should be there")

class PaddingUds(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay_padding(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_8.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(1, "s")
        time.sleep(2)
        index = 3
        ret = self.CANEngine.call_module(index, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 20, "Should be 20 groups of packets")
        self.assertTrue(1790 in _bodyList, "1790 should be there")
        self.assertTrue(1791 in _bodyList, "1791 should be there")
        self.assertTrue(1792 in _bodyList, "1792 should be there")
        self.assertTrue((8, bytes.fromhex("02010d4141414141"), "USBTin", False) in _bodyList[1792], "020902 as packet should be there")
        self.assertTrue((8, bytes.fromhex("062f030703000041"), "USBTin", False) in _bodyList[1792],
                        "062f0307030000 as packet should be there")
        self.assertTrue((8, bytes.fromhex("0209024141414141"), "USBTin", False) in _bodyList[1792], "020901 as packet should be there")
        self.assertTrue((8, bytes.fromhex("02010d4141414141"), "USBTin", False) in _bodyList[1790], "02010d as packet should be there")
        self.assertFalse((8, bytes.fromhex("0209044141414141"), "USBTin", False) in _bodyList[1791],
                         "020904 as packet should not be there")

        self.CANEngine.call_module(2, "r")
        time.sleep(2)
        ret = self.CANEngine.call_module(3, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(3, "a")
        print(ret)
        self.assertTrue(1 == _bodyList[1800][(
            8,
            bytes.fromhex("1014490201314731"),
            "USBTin",
            False
        )], "Should be 1 packed replayed")

        self.assertTrue(0 < ret.find("ASCII: .1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("Response: 00"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("ASCII: I..1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("DATA: 4902013147315a54353338323646313039313439"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("ID: 0x701 Service: 0x2f Sub: 0x3 (Input Output Control By Identifier)"), "Text should be found in response")
        self.assertTrue(0 < ret.find("ID: 0x6ff Service: 0x1 Sub: 0xd (Req Current Powertrain)"), "Text should be found in response")

class ModUsbTin(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_usbtin(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_7.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(1, "r")
        self.CANEngine.call_module(3, "t T112233446112233445566")
        time.sleep(1)
        ret = self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[2][1]._bodyList
        self.assertTrue( 6 == len(_bodyList),"6 uiniq ID, should be sent")
        self.assertTrue(0 < ret.find(" 0x2bc "), "Message should be in the list")
        self.assertTrue(0 < ret.find(" 2f410d0011223344 "), "Message should be in the list")
        self.assertTrue(0 < ret.find(" 112233445566"), "Message should be in the list")
        self.assertTrue(0 < ret.find(" 0x11223344 "), "Message should be in the list")




class ModStatDiffTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_diff(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-3")
        time.sleep(1)
        self.CANEngine.call_module(1, "D")
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-3")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "I")
        self.assertFalse(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x709 "), "Should be empty diff")
        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)

        ret = self.CANEngine.call_module(1, "I")
        print(ret)
        self.assertTrue(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 < ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 < ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x709 "), "Should be empty diff")

        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)

        ret = self.CANEngine.call_module(1, "N ")
        self.assertTrue(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 < ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 < ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x709 "), "Should be empty diff")

        self.CANEngine.call_module(1, "D, TEST BUFF")
        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)
        self.CANEngine.call_module(1, "D, TEST BUFF2")
        self.CANEngine.call_module(0, "r")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "I 2,3")
        self.assertFalse(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 < ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 < ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "I 2,3,2")
        self.assertFalse(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 < ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "I 2,3,3")
        self.assertFalse(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 < ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 < ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "N")
        self.assertFalse(0 < ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 < ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 < ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 < ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 < ret.find("2246313039313439"), "Should not be empty diff")


class LibDefragTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")


    def test_meta_add(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "l tests/replay.save")
        self.CANEngine.call_module(0, "r 0-21")
        time.sleep(2)
        mod_stat = 1
        ret = self.CANEngine.call_module(mod_stat, "a")
        print(ret)

        idx2 = ret.find("ID 0x7a6b and length 28")
        idx3 = ret.find("ID 0x7a6a and length 14")
        idx = ret.find("ID 0x7a6c and length 6")

        self.assertTrue(0 < idx2, "Comment 'ID 31339' should be found ")
        self.assertTrue(0 < idx3, "Comment 'ID 31338' should  be found ")
        self.assertFalse(0 < idx, "Comment 'ID 31338' should NOT be found 3 times")

class ModStatMetaTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_meta_add(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        mod_stat = 1
        #self.CANEngine.call_module(mod_stat, "i 1800, .*13039313439, TEST_UDS2")
        self.CANEngine.call_module(mod_stat, "i 0x708 ,.*, TEST UDS")
        self.CANEngine.call_module(mod_stat, "i 0x2bc , 0f410d00 , TEST 700")
        self.CANEngine.call_module(mod_stat, "i 1803 , 2f............44 , TEST 1803")
        self.CANEngine.call_module(mod_stat, "i 1801 , 036f , TEST 1801")

        self.CANEngine.call_module(mod_stat, "z tests/meta.txt")
        ret = self.CANEngine.call_module(mod_stat, "p")
        print(ret)
        idx = ret.find("TEST UDS")
        self.assertTrue(0 < idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 < idx2, "Comment 'TEST UDS' should be found 2 times")
        #idx3 = ret.find("TEST_UDS2", idx2 + 8)
        self.assertTrue(0 < ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 < ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 < ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")


    def test_meta_add2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        mod_stat = 1
        ret = self.CANEngine.call_module(mod_stat, "p")
        idx = ret.find("TEST UDS")
        self.assertTrue(-1 == idx, "Comment 'TEST UDS' should NOT be found")
        self.CANEngine.call_module(mod_stat, "l tests/meta.txt")
        ret = self.CANEngine.call_module(mod_stat, "p")
        print(ret)
        idx = ret.find("TEST UDS")
        self.assertTrue(0 < idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 < idx2, "Comment 'TEST UDS' should be found 2 times")
        #idx3 = ret.find("TEST_UDS2", idx2 + 8)
        #self.assertTrue(0 < idx3, "Comment 'TEST UDS' should be found 3 times")
        self.assertTrue(0 < ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 < ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 < ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")

class ModFuzzTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_fuzz_can(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_6.py")
        self.CANEngine.edit_module(0, {'id': [111], 'data': [0,1], 'delay': 0})
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        # print ret
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue( 511 == len(_bodyList[111]),"511 uiniq packets, should be sent")

    def test_fuzz_iso(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_6.py")
        self.CANEngine.edit_module(0, {'id': [[111,112]], 'data': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],\
                                       'delay': 0,'index':[5,16],'mode':'ISO'})
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        # print ret
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(513 == len(_bodyList[111]),"513 uiniq packets, should be sent")

class ModUdsTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay1(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(2, "s")
        time.sleep(2)
        index = 1
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 20, "Should be 20 groups of packets")
        self.assertTrue(1790 in _bodyList, "1790 should be there")
        self.assertTrue(1791 in _bodyList, "1791 should be there")
        self.assertTrue(1792 in _bodyList, "1792 should be there")
        self.assertTrue((3, bytes.fromhex("02010d"), "Default", False) in _bodyList[1792], "020902 as packet should be there")
        self.assertTrue((7, bytes.fromhex("062f0307030000"), "Default", False) in _bodyList[1792],
                        "062f0307030000 as packet should be there")
        self.assertTrue((3, bytes.fromhex("020902"), "Default", False) in _bodyList[1792], "020901 as packet should be there")
        self.assertTrue((3, bytes.fromhex("02010d"), "Default", False) in _bodyList[1790], "02010d as packet should be there")
        self.assertFalse((3, bytes.fromhex("020904"), "Default", False) in _bodyList[1791],
                         "020904 as packet should not be there")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(1, "a")
        print(ret)
        self.assertTrue(1 == _bodyList[1800][(
            8,
            bytes.fromhex("1014490201314731"),
            "Default",
            False
        )], "Should be 1 packed replayed")

        self.assertTrue(0 < ret.find("ASCII: .1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("Response: 00"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("ASCII: I..1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("DATA: 4902013147315a54353338323646313039313439"), "TEXT should be found in response")
        self.assertTrue(0 < ret.find("ID: 0x701 Service: 0x2f Sub: 0x3 (Input Output Control By Identifier)"), "Text should be found in response")
        self.assertTrue(0 < ret.find("ID: 0x6ff Service: 0x1 Sub: 0xd (Req Current Powertrain)"), "Text should be found in response")

class ModReplayTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay1(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_3.py")
        self.CANEngine.start_loop()
        time.sleep(2)
        self.CANEngine.call_module(2, "s")
        num = self.CANEngine.call_module(1, "p")
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be be 0 packets")
        self.CANEngine.call_module(1, "g")
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 666:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 5:8:1122334411111111")
        time.sleep(1)
        num = self.CANEngine.call_module(1, "p")

        #print("num is " + num)
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be be 4 packets")
        self.CANEngine.call_module(1, "g")
        ret = self.CANEngine.call_module(1, "d 0-4")
        time.sleep(1)
        print(ret)
        self.CANEngine.call_module(2, "s")
        time.sleep(1)
        self.CANEngine.call_module(1, "r 0-4")
        time.sleep(1)
        self.CANEngine.call_module(1, "c")
        time.sleep(1)
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be be 0 packets")
        index = 2
        ret = self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        print(ret)
        time.sleep(1)
        self.assertTrue(len(_bodyList) == 3, "Should be be 3 groups found")

    def test_replay2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_4.py")
        self.CANEngine.start_loop()
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be be 4 packets")
        index = 2
        self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be 0 packets sent")
        self.CANEngine.call_module(1, "r 2-4")
        time.sleep(1)

        ret = self.CANEngine.call_module(2, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(2 == len(_bodyList), "Should be 2 packets sent")
        self.assertTrue(666 in _bodyList, "ID 666 should be dound")
        self.assertTrue(5 in _bodyList, "ID 5 should be found")
        self.assertFalse(4 in _bodyList, "ID 4 should not be found ")
        self.CANEngine.call_module(2, "r tests/new.save")
        self.CANEngine.call_module(2, "c")
        self.CANEngine.call_module(1, "l tests/new.save")
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.assertTrue(0 <= ret.find("Loaded packets: 6"), "Should be 6 packets")


class ModPingTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_isoanal(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'range': [542999, 543002],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.edit_module(1, {
            'pipe': 1,
            'range': [543002, 543005],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233'
        })
        self.CANEngine.start_loop()
        time.sleep(2)
        self.CANEngine.call_module(0, "s")
        self.CANEngine.call_module(1, "s")
        time.sleep(1)
        ret = self.CANEngine.call_module(3, "p")
        print(ret)
        ret = self.CANEngine.call_module(3, "a")
        print(ret)
        self.assertTrue(ret.find("ID: 0x84917") > 0, "Should be be found 542999")
        self.assertTrue(ret.find("ID: 0x84918") > 0, "Should be found 543000")
        self.assertFalse(ret.find("ID: 0x8491a") > 0, "Should not be found 543002")

    def test_emptyConfig(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        self.CANEngine.call_module(0, "s")
        time.sleep(1)
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be empty list")

    def test_ping(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'range': [542999, 543002],
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(1)
        index = 3

        ret = self.CANEngine.call_module(3, "p")

        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(543000 in _bodyList, "We should be able to find ID 543000")
        self.assertFalse(543002 in _bodyList, "We should not be able to find ID 543002")
        self.assertTrue([1, 1, 1, 1, 1, 1] == list(_bodyList[543001].values()), "We should not be able to find ID")
        self.assertTrue(
            "25112233" == (codecs.encode((list(_bodyList[543001].keys())[5][1]), 'hex_codec')).decode("ISO-8859-1"),
            "Last packet of sec should be like that"
        )
        self.assertTrue(
            "24a1a2a3a4a5a6a7" == (codecs.encode((list(_bodyList[543001].keys())[4][1]), 'hex_codec')).decode("ISO-8859-1") ,
            "Last packet of sec should be like that"
        )


class ModStatTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_stat(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.conf")
        self.CANEngine.edit_module(1, {'pipe': 2})
        time.sleep(1)
        self.CANEngine.start_loop()
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 455678:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:1122334455")
        time.sleep(1)
        index = 1

        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue(455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse(2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse(0 in _bodyList, "We should not be able to find ID 0")

        self.CANEngine.call_module(1, "c")
        self.CANEngine.call_module(0, "t 2:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.call_module(1, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertFalse(4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse(455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue(2 in _bodyList, "We should be able to find ID 2")


class ModFirewallTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_blockedBody(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.py")
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_body': [[1, 2, 3, 6, 5]]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, "t 4:6:010203060505")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:5:0102030605")  # blocked

        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod is None, "We should NOT find message in PIPE")
        #self.assertFalse(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.edit_module(2, {'pipe': 2, 'white_body': [[1, 2, 3, 6, 5]]})

        self.CANEngine.call_module(0, "t 4:5:0102030605")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:6:010203060505")  # blocked

        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod is None, "We should NOT find message in PIPE")
        #self.assertFalse(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

    def test_blockedID(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.py")
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_list': [1, 2, 3, 6, 5]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 7:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod.frame_id == 7, "We should be able to find ID 7")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:8:1122334411223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

if __name__ == '__main__':
    sys.path.append('./modules')
    from libs.engine import *
    from libs.can import *
    from libs.module import *

    # absPath=os.path.dirname(platform_audit) + "/unit_tests/"
    unittest.main()
else:
    from libs.engine import *
    from libs.can import *
    from libs.module import *
