from mpl_format.axes.axes_formatter import AxesFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from numpy import arange, ndarray, histogram
from pandas import Series, DataFrame
from typing import Optional

from survey.compound_types import Bins
from survey.mixins.data_types.numerical_1d_mixin import Numerical1dMixin
from survey.utils.plots import label_bar_plot_pcts


class Discrete1dMixin(Numerical1dMixin):

    @staticmethod
    def _default_hist(data: Series) -> ndarray:
        min_val = data.min()
        max_val = data.max()
        if min_val <= max_val / 10:
            return arange(-0.5, max_val + 1.5)
        else:
            return arange(min_val - 0.5, max_val + 1.5)

    def plot_distribution(
            self, data: Optional[Series] = None,
            transpose: bool = False,
            bins: Optional[Bins] = None,
            color: str = 'C0', pct_size: int = None,
            grid: bool = False,
            title: Optional[str] = None,
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            ax: Optional[Axes] = None
    ) -> Axes:
        """
        Plot a histogram of the distribution of the response data.

        :param data: The answers given by Respondents to the Question.
        :param transpose: True to plot horizontally.
        :param bins: Value for hist bins. Leave as None for integer bins.
        :param color: Color or list of colors for the bars.
        :param pct_size: Font size for the percent markers.
        :param grid: Whether to show a plot grid or not.
        :param title: Optional title for the plot.
        :param x_label: Label for the x-axis.
        :param y_label: Label for the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        ax = ax or new_axes()
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        orientation = 'horizontal' if transpose else 'vertical'
        bins = bins or self._default_hist(data)
        data.plot(kind='hist', ax=ax, bins=bins, orientation=orientation,
                  color=color)

        # add percentages
        hist, edges = histogram(data, bins=bins)
        item_counts = Series(
            index=0.5 * (edges[1:] + edges[:-1]),
            data=hist
        )
        item_pcts = 100 * item_counts / item_counts.sum()
        label_bar_plot_pcts(item_counts=item_counts, item_pcts=item_pcts,
                            ax=ax, transpose=transpose, font_size=pct_size)

        # add titles and grid
        ax.set_title(self.text)
        AxesFormatter(ax).set_text(
            title=title, x_label=x_label, y_label=y_label
        ).set_axis_below(True).grid(grid)
        if transpose and not x_label:
            ax.set_xlabel('# Respondents')
        elif not transpose and not y_label:
            ax.set_ylabel('# Respondents')

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

    def unique(self) -> list:

        return sorted(self._data.unique())
