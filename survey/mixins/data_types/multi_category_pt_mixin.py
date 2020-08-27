from matplotlib.axes import Axes
from pandas import Series
from typing import List

from survey.utils.plots import plot_pt
from survey.utils.probability.prob_utils import create_jpt, create_cpt


class MultiCategoryPTMixin(object):

    data: Series
    categories: List[str]
    name: str

    def plot_jpt(self, other: 'MultiCategoryPTMixin', **kwargs) -> Axes:
        """
        Plot a joint probability table of self and other.

        :param other: Another MultiCategoryPTMixin to plot against.
        :param kwargs: See utils.plots.plot_pt
        """
        if isinstance(other, MultiCategoryPTMixin):
            other_data = other.make_features(naming='{{choice}}')
        else:
            # assume single category
            other_data = other.data
        jpt = create_jpt(
            data_1=self.make_features(naming='{{choice}}'),
            data_2=other_data,
            prob_1_name=self.name, prob_2_name=other.name,
            prob_1_order=self.categories, prob_2_order=other.categories
        )
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = False
        if 'var_sep' not in kwargs.keys():
            kwargs['var_sep'] = ','
        if 'dividers' not in kwargs.keys():
            kwargs['dividers'] = False
        ax = plot_pt(pt=jpt, **kwargs)
        return ax

    def plot_cpt(self, condition: 'MultiCategoryPTMixin', **kwargs) -> Axes:
        """
        Plot a conditional probability table of self and other.

        :param condition: Another MultiCategoryPTMixin to condition on.
        :param kwargs: See utils.plots.plot_pt
        """
        if isinstance(condition, MultiCategoryPTMixin):
            cond_data = condition.make_features(naming='{{choice}}')
        else:
            # assume single category
            cond_data = condition.data
        jpt = create_cpt(
            prob_data=self.make_features(naming='{{choice}}'),
            cond_data=cond_data,
            prob_name=self.name, cond_name=condition.name,
            prob_order=self.categories, cond_order=condition.categories
        )
        if 'var_sep' not in kwargs.keys():
            kwargs['var_sep'] = '|'
        ax = plot_pt(pt=jpt, **kwargs)
        return ax
