from typing import Dict, Any

from pandas import DataFrame

from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin


class SingleCategoryGroupComparisonMixin(object):

    item_dict: Dict[str, SingleCategoryMixin]
    __getitem__: Any

    def __gt__(self, other: 'SingleCategoryGroupComparisonMixin') -> DataFrame:
        """
        Find the probability that each answer is more likely to be selected for
        each pair of questions in this and the other group.
        """
        results = {}
        for key in self.item_dict.keys():
            results[key] = self[key] > other[key]
        return DataFrame(results)

    def __lt__(self, other: 'SingleCategoryGroupComparisonMixin') -> DataFrame:
        """
        Find the probability that each answer is more likely to be selected for
        each pair of questions in this and the other group.
        """
        return other.__gt__(self)
