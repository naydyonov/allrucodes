from .basecodes import BaseCodes


class OKOPFCodes(BaseCodes):
    def __init__(self) -> None:
        super().__init__(
            "okopf.pkl", dict_search_fields=["name"], partial_search_fields=["name"]
        )
