import unittest
from allrucodes import OKSMCodes


class TestOKSMCodes(unittest.TestCase):       
    def test_dict_search(self):
        test_values = {'ru':643, 'RU':643, 'Россия':643, 'UA':804}
        oksm = OKSMCodes()
        for value, code in test_values.items():
            self.assertEqual(oksm._find_in_dict_search_fields(value.lower()), code, value)
            
    def test_full_search(self):
        test_values = {'RU':643, 'Россия':643, 'UA':804, 'Рос сия':643}
        oksm = OKSMCodes()
        for value, code in test_values.items():
            self.assertEqual(oksm.find_by_value(value), code, value)
