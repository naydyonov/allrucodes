import pickle
import pkgutil
import logging

import numpy as np
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseCodes:
    def __init__(
        self,
        codes_file: str,
        code_key: str = "code",
        dict_search_fields=None,
        partial_search_fields=None,
    ) -> None:
        """Base class for containing codes catalogs

        Args:
            codes_file (str): pickle file which contains codes data
                in format of list of dicts
            code_key (str, optional): field in data which containes code id.
                Defaults to 'code'.
            dict_search_fields (_type_, optional): Fields used for fast search
                as dict keys.
                Defaults to None.
            partial_search_fields (_type_, optional): Fields used for slower
                but more accurate partial and fuzzy search.
                Defaults to None.
        """

        assert codes_file != "", "no empty directory_file str is allowed"
        assert isinstance(code_key, str)
        assert code_key != ""

        self._codes_data = pickle.loads(
            pkgutil.get_data(__name__, f"data/{codes_file}")
        )
        self._code_key = code_key
        self._dict_search_fields = dict_search_fields
        self._partial_search_fields = partial_search_fields

        if self._codes_data is None:
            raise AssertionError("Data directory is empty!")
        if not isinstance(self._codes_data, list):
            raise TypeError("Codes data should be a list!")

        self.code2entities = {
            row[code_key]: {k: v for k, v in row.items() if k != code_key}
            for row in self._codes_data
        }

        # TODO: change name of dict to partial_search_fields
        self.entities2code = {}
        if self._partial_search_fields:
            for row in self._codes_data:
                for field, field_value in row.items():
                    if (
                        field_value is None
                        or field_value is np.nan
                        or field_value == ""
                        or field_value != field_value
                    ):
                        continue
                    # TODO: should we check duplication of field_value in dict?
                    if field in self._partial_search_fields:
                        self.entities2code[field_value.lower()] = row[self._code_key]

        # we create dict for every dict_field for fast dict search
        if self._dict_search_fields is not None:
            self._dict_for_search = {}
            for field in self._dict_search_fields:
                self._dict_for_search[field] = {
                    row[field].lower(): row[self._code_key]
                    for row in self._codes_data
                    if not self._isnan(row[field])  # check for nan
                }

    def get(self, code: str):
        return self.code2entities.get(code, None)

    def find_by_value(
        self,
        value: str,
        no_fuzzy_search=True,
        fuzzy_search_threshold=0.9,
        fuzzy_seach_type: str = "first",
        default_value=None,
    ):
        if not isinstance(value, str):
            raise TypeError("Only str type value is allowed")

        # find lower case
        value = value.lower()

        if not isinstance(value, str):
            raise TypeError(f"value {value} should be str type")

        strict_result = self._find_in_dict_search_fields(value)
        if strict_result is not None:
            logger.debug(f"strict found {strict_result}")
            return strict_result

        partial_result = self._find_partial(value)
        if partial_result:
            logger.debug(f"partial found {partial_result}")
            return partial_result

        if not no_fuzzy_search:
            fuzzy_result = self._find_fuzzy(
                value=value,
                fuzzy_search_threshold=fuzzy_search_threshold,
                fuzzy_seach_type=fuzzy_seach_type,
            )
            if fuzzy_result:
                logger.debug(f"fuzzy found {fuzzy_result}")
                return fuzzy_result

        # Nothing found
        return default_value

    def _find_in_dict_search_fields(self, value):
        for field in self._dict_search_fields:
            if value in self._dict_for_search[field].keys():
                return self._dict_for_search[field][value]
        return None

    def _find_partial(self, value: str):
        for field_value, code in self.entities2code.items():
            if field_value.find(value) > -1:
                return code
        return None

    def _find_fuzzy(
        self, value: str, fuzzy_search_threshold=0.9, fuzzy_seach_type: str = "first"
    ):
        # TODO: check if it necessary here - who's responsibility?
        if not self._partial_search_fields:
            return None

        # convert to value for fuzzywuzzy usage
        fuzzy_search_threshold = fuzzy_search_threshold * 100

        max_dist = 0
        best = None
        count = 0
        variants = []

        for field_value, code in self.entities2code.items():
            cur_dist = fuzz.partial_ratio(field_value, value)
            if cur_dist >= fuzzy_search_threshold:
                count += 1

                if cur_dist > max_dist:
                    max_dist = cur_dist
                    best = code
                    variants.append((best, cur_dist))

                if fuzzy_seach_type == "first":
                    logger.debug(f"fuzzy first found {best}, dist: {max_dist}")
                    break

        if fuzzy_seach_type == "best":
            logger.debug(f"fuzzy found {count} variants")
            logger.debug(f"fuzzy best found {best}, dist: {max_dist}")
            logger.debug(f"variants: {variants}")

        return best

    def _isnan(self, value):
        if value != value or value is None or value is np.nan:
            return True
        else:
            return False
