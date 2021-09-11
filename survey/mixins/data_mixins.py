from typing import Callable, Optional

from numpy import nan
from pandas import Series, isnull, Interval
from pandas.core.dtypes.inference import is_number


class ObjectDataMixin(object):

    _data: Optional[Series]
    _validate_data: Callable[[Series], None]

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


class NumericDataMixin(object):

    _data: Optional[Series]
    _validate_data: Callable[[Series], None]

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
            try:
                data = data.astype(int)
            except ValueError:
                data = data.astype(float)
            self._data = data


class SingleCategoryDataMixin(object):

    _data: Optional[Series]
    name: str
    _validate_data: Callable[[Series], None]

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
            data = Series(
                index=data.index,
                data=[nan if isnull(d)
                      else d if type(d) is str
                      else d if type(d) is Interval
                      else str(int(d)) if is_number(d) and d == int(d)
                      else str(d)
                      for d in data.values],
                name=self.name
            ).astype('category')
            self._validate_data(data)
            self._data = data


class MultiCategoryDataMixin(object):

    _data: Optional[Series]
    name: str
    _validate_data: Callable[[Series], None]

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
            data = Series(
                index=data.index,
                data=[
                    nan if isnull(d)
                    else nan if type(d) is str and d == ''
                    else d if type(d) is str
                    else str(d)
                    for d in data.values
                ],
                name=self.name
            )
            self._validate_data(data)
            self._data = data
