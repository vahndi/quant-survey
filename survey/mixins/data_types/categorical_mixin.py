from typing import Union, List, Dict, Optional

from pandas import Series

from survey.compound_types import GroupPairs
from survey.utils.processing import get_group_pairs


class CategoricalMixin(object):

    _categories:  Union[List[str], Dict[str, int]]
    _ordered: bool
    _data: Series
    name: str

    def _set_categories(self, categories: Union[List[str], Dict[str, int]]):

        self._categories = categories

    @property
    def categories(self) -> Union[List[str], Dict[str, int]]:
        return self._categories

    def unique(self) -> list:

        values = self._data.unique()
        return [cat for cat in self._categories if cat in values]

    @property
    def category_names(self) -> List[str]:
        if isinstance(self._categories, list):
            return self._categories
        elif isinstance(self._categories, dict):
            return list(self._categories.keys())
        else:
            raise TypeError()

    @property
    def category_values(self) -> list:
        if isinstance(self._categories, list):
            return self._categories
        elif isinstance(self._categories, dict):
            return list(self._categories.values())
        else:
            raise TypeError()

    def group_pairs(self, ordered: Optional[bool] = None) -> GroupPairs:
        """
        Return all pairs of groups of answer choices
        e.g. for (a, b, c) return [(a, [b, c]), ([a, b], c), ([a, c], b)]

        :param ordered: Whether to return ordered pairs only.
                        If not specified, use the `_ordered` property of the
                        Categorical item.
        """
        ordered = ordered if ordered is not None else self._ordered
        if ordered:
            return get_group_pairs(
                items=self.category_names,
                ordered=True, include_empty=False
            )
        else:
            return get_group_pairs(
                items=self.category_names,
                ordered=False, include_empty=False
            )

    @property
    def ordered(self) -> bool:
        return self._ordered
