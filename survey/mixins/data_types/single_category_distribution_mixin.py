from matplotlib.axes import Axes
from pandas import Series, DataFrame
from typing import Tuple, List, Callable, Optional

from survey.utils.plots import plot_categorical_distribution


class SingleCategoryDistributionMixin(object):

    data: Series
    category_names: List[str]
    text: str
    significance_one_vs_any: Callable[[], Series]

    def plot_distribution(self, data: Optional[Series] = None, color: str = 'C0',
                          significance: bool = False,
                          sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                          ** kwargs) -> Axes:
        """
        Plot the distribution of answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param color: Color or list of colors for the bar faces.
        :param significance: Whether to highlight significant categories.
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
        :param kwargs: See survey.utils.plots.plot_categorical_distribution
        """
        data = data if data is not None else self.data
        if data is None:
            raise ValueError('No data!')
        if 'order' not in kwargs.keys():
            kwargs['order'] = self.category_names
        if 'transpose' not in kwargs.keys():
            kwargs['transpose'] = False
        if 'title' not in kwargs.keys():
            kwargs['title'] = self.text

        edge_color = None
        line_width = None
        if significance:
            one_vs_any = self.significance_one_vs_any()
            edge_color = [sig_colors[0] if one_vs_any[category] >= 0.945 else
                          sig_colors[1] if one_vs_any[category] < 0.055 else
                          color for category in self.category_names]
            line_width = [2 if ec != color else None for ec in edge_color]

        ax = plot_categorical_distribution(
            categorical_data=data,
            color=color, edge_color=edge_color,
            line_width=line_width,
            **kwargs
        )

        return ax

    def distribution_table(self, data: Optional[Series] = None,
                           significance: bool = False) -> DataFrame:
        """
        Get the distribution of answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param significance: Whether to calculate significant categories.
        """
        data = data if data is not None else self.data
        if data is None:
            raise ValueError('No data!')
        item_counts: Series = data.value_counts()
        item_counts = item_counts.reindex(
            self.category_names
        ).fillna(0).astype(int)
        item_counts.index.name = 'Value'
        item_counts.name = 'Count'
        table: DataFrame = item_counts.to_frame()
        if significance:
            table['Significance'] = self.significance_one_vs_any()
        table = table.reset_index()
        return table
