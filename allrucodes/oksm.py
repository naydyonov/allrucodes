import pickle
#import pkgutil
from basecodes import BaseCodes


class OKSMCodes(BaseCodes):
    def __init__(self):
        super().__init__('oksm.pkl', 
                         dict_search_fields=['alfa2',
                                             'alfa3',
                                             'shortname_ru',
                                             'shortname_en',
                                             'fullname_ru',
                                             'fullname_en'])
        self.code2country = {row['code']: {k:v for k,v in row.items() if k!='code'}
                             for row in self.directory}
