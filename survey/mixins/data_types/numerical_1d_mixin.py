from pandas import Series
from typing import Optional


class Numerical1dMixin(object):
    _data: Series
    name: str
    text: str

    def make_features(self, data: Optional[Series] = None, normalize: bool = True) -> Series:
        if data is None:
            data = self._data
        if normalize:
            return (data - data.min()) / (data.max() - data.min())
        else:
            return data