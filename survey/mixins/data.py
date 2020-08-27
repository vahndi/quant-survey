from typing import List

from numpy import nan
from pandas import Series, isnull
from pandas.core.dtypes.inference import is_number

from survey.constants import CATEGORY_SPLITTER


class DataMixin(object):

    _data: Series

    def _set_data(self, data: Series):

        self.data = data

    @property
    def data(self) -> Series:
        return self._data

    @data.setter
    def data(self, data: Series):
        if data is None:
            self._data = None
        else:
            self._validate_data(data)
            self._data = data


class CategoricalDataMixin(object):

    _data: Series
    name: str

    def _set_data(self, data: Series):
        if data is not None:
            self.data = data

    @property
    def data(self) -> Series:
        return self._data

    @data.setter
    def data(self, data: Series):
        if data is None:
            self._data = None
        else:
            self._validate_data(data)
            self._data = Series(
                index=data.index,
                data=[nan if isnull(d)
                      else d if type(d) is str
                      else str(int(d)) if is_number(d) and d == int(d)
                      else str(d)
                      for d in data.values],
                name=self.name
            )
