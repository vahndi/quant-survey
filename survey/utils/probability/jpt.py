from mpl_toolkits.axes_grid1.mpl_axes import Axes
from pandas import merge, DataFrame

from survey.mixins.data_types.single_category_mixin import SingleCategoryMixin
from survey.utils.plots import plot_pt
from survey.utils.probability.prob_utils import create_jpt


class JPT(object):
    """
    Represents a Conditional Probability Table of 2 variables.
    """
    def __init__(self, prob_1: SingleCategoryMixin,
                 prob_2: SingleCategoryMixin):

        self._prob_1 = prob_1
        self._prob_2 = prob_2
        self._instances = merge(left=prob_1.data.rename(prob_1.name),
                                right=prob_2.data.rename(prob_2.name),
                                left_index=True, right_index=True, how='inner')
        self._data = create_jpt(data_1=prob_1.data, data_2=prob_2.data,
                                prob_1_order=prob_1.category_names,
                                prob_2_order=prob_2.category_names)

    @property
    def data(self) -> DataFrame:
        return self._data

    def plot_distribution(self, **kwargs) -> Axes:
        """
        Plot the Joint Probability Table as a heatmap.

        :param kwargs: See utils.plots.plot_pt
        """
        # calculate create_cpt and fix labels
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = True
        if 'var_sep' not in kwargs:
            kwargs['var_sep'] = ','
        if 'dividers' not in kwargs:
            kwargs['dividers'] = False
        ax = plot_pt(pt=self._data, **kwargs)
        return ax
