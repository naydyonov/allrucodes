import logging

from .basecodes import BaseCodes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OKOPFCodes(BaseCodes):
    def __init__(self) -> None:
        super().__init__(
            "okopf.pkl", dict_search_fields=["name"], partial_search_fields=["name"]
        )
