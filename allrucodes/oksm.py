import logging

# import pkgutil
from .basecodes import BaseCodes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OKSMCodes(BaseCodes):
    def __init__(self):
        super().__init__(
            "oksm.pkl",
            dict_search_fields=[
                "alfa2",
                "alfa3",
                "shortname_ru",
                "shortname_en",
                "fullname_ru",
                "fullname_en",
            ],
            partial_search_fields=[
                "alfa2",
                "alfa3",
                "shortname_ru",
                "shortname_en",
                "fullname_ru",
                "fullname_en",
            ],
        )
