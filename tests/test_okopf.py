import unittest
from allrucodes import OKOPFCodes


class TestOKSMCodes(unittest.TestCase):                   
    def test_full_search(self):
        test_values = {'акционерного общества': '12200'}
        oksm = OKOPFCodes()
        for value, code in test_values.items():
            self.assertEqual(oksm.find_by_value(value), code, value)