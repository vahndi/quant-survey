from typing import Optional

from mpl_format.axes.axis_utils import new_axes
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from numpy import arange, histogram, ndarray
from pandas import Series, DataFrame
from seaborn import distplot

from survey.compound_types import Bins
from survey.mixins.data_types.numerical_1d_mixin import Numerical1dMixin


class Continuous1dMixin(Numerical1dMixin):

    name: str
    text: str

    @staticmethod
    def _default_hist(data: Series) -> ndarray:
        return arange(-0.5, data.max() + 1.5)

    def plot_distribution(self, data: Optional[Series] = None,
                          transpose: bool = False,
                          ax: Optional[Axes] = None) -> Axes:
        """
        Plot the distribution of answers to the Question.

        :param data: Optional response data. Required if the Question does not
                     already have any.
        :param transpose: True to plot vertically.
        :param ax: Optional matplotlib axes to plot on.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        ax = ax or new_axes()
        distplot(a=data.dropna(),
                 rug=True, kde=True, hist=False,
                 vertical=transpose, ax=ax)
        min_val = data.min()
        max_val = data.max()

        # add titles
        ax.set_title(self.text)
        if transpose:
            ax.set_xlabel('# Respondents')
            ax.set_ylabel(self.name)
        else:
            ax.set_xlabel(self.name)
            ax.set_ylabel('# Respondents')

        # format axes
        if transpose:
            ax.set_xticks([])
            if min_val <= max_val / 10:
                ax.set_ylim(0, ax.get_ylim()[1])
        else:
            ax.set_yticks([])
            if min_val <= max_val / 10:
                ax.set_xlim(0, ax.get_xlim()[1])

        return ax

    def distribution_table(
        self, data: Optional[Series] = None,
        bins: Optional[Bins] = None,
        count: bool = True,
        percent: bool = False,
    ) -> DataFrame:
        """
        Create a histogram table of the distribution of data.

        :param data: The answers given by Respondents to the Question.
        :param bins: Value for hist bins. Leave as None for integer bins.
        :param count: Whether to include counts of each histogram bin.
        :param percent: Whether to include percentages of each histogram bin.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        bins = bins or self._default_hist(data)
        hist, bins = histogram(data, bins)
        counts = []
        total = hist.sum()
        for v, val in enumerate(hist):
            counts.append({
                'From Value': bins[v],
                'To Value': bins[v + 1],
                'Count': val,
                'Percentage': val / total
            })
        count_data = DataFrame(counts)
        cols = ['From Value', 'To Value']
        if count:
            cols.append('Count')
        if percent:
            cols.append('Percentage')
        count_data = count_data[cols]

        return count_data
