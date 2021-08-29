from collections import OrderedDict
from pandas import DataFrame
from typing import Dict, Any

from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin


class SingleCategoryGroupSignificanceMixin(object):

    __getitem__: Any

    @property
    def item_dict(self) -> Dict[str, SingleCategoryMixin]:
        raise NotImplementedError

    def significance_one_vs_all(self) -> DataFrame:
        """
        For each question in the group, return the probability that each
        response is answered at a significantly higher rate than a randomly
        selected other response.
        """
        probs = OrderedDict()
        for key in self.item_dict.keys():
            probs[key] = self[key].significance_one_vs_all()
        return DataFrame(probs)

    def significance_one_vs_any(self) -> DataFrame:
        """
        For each question in the group, return the probability that each
        response is answered at a significantly higher rate than all others
        combined.
        """
        probs = OrderedDict()
        for key in self.item_dict.keys():
            probs[key] = self[key].significance_one_vs_any()
        return DataFrame(probs)
