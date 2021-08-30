from typing import Optional

from mpl_format.axes import AxesFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from numpy import arange, histogram, ndarray
from pandas import Series, DataFrame
from seaborn import distplot, kdeplot

from survey.compound_types import Bins
from survey.mixins.data_types.numerical_1d_mixin import Numerical1dMixin
from survey.mixins.data_types.single_category_pt_mixin import \
    SingleCategoryPTMixin


class Continuous1dMixin(Numerical1dMixin):

    name: str
    text: str

    @staticmethod
    def _default_hist(data: Series) -> ndarray:
        return arange(-0.5, data.max() + 1.5)

    def plot_distribution(self, data: Optional[Series] = None,
                          transpose: bool = False,
                          ax: Optional[Axes] = None,
                          rug: Optional[bool] = True,
                          kde: Optional[bool] = True,
                          hist: Optional[bool] =False,
                          max_pct: float = 1.0,
                          **kwargs) -> Axes:
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
        a = data.dropna()
        if max_pct < 1:
            a = a.loc[a <= a.quantile(max_pct)]
        distplot(a=a,
                 rug=rug, kde=kde,
                 hist=hist,
                 vertical=transpose, ax=ax,
                 **kwargs)
        min_val = a.min()
        max_val = a.max()

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

    def plot_cpd(self, condition: SingleCategoryPTMixin,
                 max_pct: float = 1.0,
                 ax: Optional[Axes] = None,
                 **kwargs):
        """
        Plot distributions of answers to the question, conditioned on the
        values of discrete distribution `condition`.
        """
        axf = AxesFormatter(axes=ax)
        a_ix = self._data.index
        if max_pct < 1:
            a_ix = self._data.loc[
                self._data <= self._data.quantile(max_pct)].index
        a = self._data.loc[a_ix]
        condition_data = condition.data.loc[a_ix]
        kdeplot(x=a,
                hue=condition_data,
                ax=ax, **kwargs)

        # for condition_value in condition.category_names:
        #     condition_data = condition.data.loc[a_ix]
        #     condition_ix = (condition_data == condition_value).index
        #     kdeplot(x=a.loc[condition_ix],
        #             hue=condition_data[condition_ix],
        #             ax=ax, label=condition_value, **kwargs)
            # distplot(a=a.loc[condition_ix],
            #          label=condition_value,
            #          rug=False, kde=True, hist=False,
            #          ax=axf.axes, **kwargs)
        axf.set_text(x_label=self.name,
                     y_label=f'P({self.name}|{condition.name})')
        return axf.axes

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
