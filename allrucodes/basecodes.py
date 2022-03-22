import pickle
import pkgutil
import numpy as np
from fuzzywuzzy import fuzz


class BaseCodes:
    def __init__(self,
                 codes_file: str,
                 code_key: str='code',
                 dict_search_fields = None,
                 partial_search_fields = None) -> None:
        """Base class for containing codes catalogs

        Args:
            codes_file (str): pickle file which contains codes data
                in format of list of dicts
            code_key (str, optional): field in data which containes code id.
                Defaults to 'code'.
            dict_search_fields (_type_, optional): Fields used for fast search
                as dict keys.
                Defaults to None.
            partial_search_fields (_type_, optional): Fields used for more slow
                partial and fuzzy search.
                Defaults to None.
        """        
        
        assert codes_file!='', 'no empty directory_file str is allowed'
        assert isinstance(code_key, str)
        assert code_key!=''

        self.codes_data = pickle.loads(pkgutil.get_data(__name__, f'data/{codes_file}'))
        self._code_key = code_key
        self._dict_search_fields = dict_search_fields
        self._partial_search_fields = partial_search_fields
        
        assert self.codes_data, 'directory is empty!'
        assert isinstance(self.codes_data, list)

        self.code2entities = {row[code_key]: {k:v for k,v in row.items() if k!=code_key}
                              for row in self.codes_data}
        
        self.entities2code = {}
        if self._partial_search_fields:
            for row in self.codes_data:
                # TODO: refactor to comprehension
                for field, field_value in row.items():
                    if field_value is None or field_value is np.nan or field_value=='':
                        continue
                    if field in self._partial_search_fields:
                        self.entities2code[field_value] = row[self._code_key]
        
        # we create dict for every dict_field for fast dict search
        if self._dict_search_fields is not None:
            self._dict_for_search = {}
            for field in self._dict_search_fields:
                self._dict_for_search[field] = {
                    row[field]: row[self._code_key] for row in self.codes_data
                }

    def get(self, code: str):
        return self.code2entities.get(code, None)

    def find_by_value(self,
                      value: str,
                      no_fuzzy_search=True,
                      fuzzy_search_threshold=0.9,
                      fuzzy_seach_type: str='first',
                      default_value=None):
        if not isinstance(value, str):
            raise TypeError(f'value {value} should be str type')
        
        strict_result = self._find_in_dict_search_fields(value)
        if strict_result:
            return strict_result
        
        partial_result = self._find_partial(value)
        if partial_result:
            return partial_result
        
        fuzzy_result = self._find_fuzzy(value=value,
                                        no_fuzzy_search=no_fuzzy_search,
                                        fuzzy_search_threshold=fuzzy_search_threshold,
                                        fuzzy_seach_type=fuzzy_seach_type,
                                        default_value=default_value)
        if fuzzy_result:
            return fuzzy_result
        
        # Nothing found
        return default_value
        

    def _find_in_dict_search_fields(self, value):
        for field in self._dict_search_fields:
            if value in self._dict_for_search[field].keys():
                return self._dict_for_search[field][value]
        return None
    
    def _find_partial(self,
                      value: str):
        for field_value, code in self.entities2code.items():
            if field_value.find(value)>-1:
                return code
        return None
    
    def _find_fuzzy(self,
                    value: str,
                    fuzzy_search_threshold=0.9,
                    fuzzy_seach_type: str='first'):
        # TODO: check if it necessary here - who's responsibility?
        if not self._partial_search_fields:
            return None
        
        max_dist = 0
        best = None
        count = 0
        
        for field_value, code in self.entities2code.items():
            cur_dist = fuzz.partial_ratio(field_value, value)
            if cur_dist>max_dist:
                max_dist = cur_dist
                best = code
                
            if cur_dist>=fuzzy_search_threshold:
                count += 1
                
            if max_dist>=fuzzy_search_threshold and fuzzy_seach_type=='first':
                break
        
        return best