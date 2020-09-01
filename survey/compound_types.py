from numpy import ndarray
from typing import List, Tuple, Union


GroupPairs = List[Tuple[List[str], List[str]]]
Bins = Union[int, ndarray, range, list]
StringOrStringTuple = Union[str, Tuple[str]]
