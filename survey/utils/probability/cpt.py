from matplotlib.axes import Axes
from pandas import merge, DataFrame

from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin
from survey.utils.plots import plot_pt
from survey.utils.probability.prob_utils import create_cpt


class CPT(object):
    """
    Represents a Conditional Probability Table of 2 variables.
    """
    def __init__(self, probability: SingleCategoryMixin,
                 condition: SingleCategoryMixin):

        self._probability = probability
        self._condition = condition
        self._instances = merge(left=probability.data.rename(probability.name),
                                right=condition.data.rename(condition.name),
                                left_index=True, right_index=True, how='inner')
        self._data = create_cpt(prob_data=probability.data,
                                cond_data=condition.data,
                                prob_name=probability.name,
                                cond_name=condition.name,
                                prob_order=probability.category_names,
                                cond_order=condition.category_names)

    @property
    def data(self) -> DataFrame:
        return self._data

    def plot_distribution(self, **kwargs) -> Axes:
        """
        Plot the Conditional Probability Table as a heatmap.

        :param kwargs: See utils.plots.plot_pt
        """
        # calculate create_cpt and fix labels
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = True
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = '|'
        ax = plot_pt(pt=self._data, **kwargs)
        return ax
