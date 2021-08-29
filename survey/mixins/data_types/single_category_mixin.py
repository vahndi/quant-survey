from typing import List, Union, Tuple, Optional, Dict

from matplotlib.patches import Patch
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from numpy import nan
from pandas import Series, DataFrame, get_dummies, concat
from probability.distributions import BetaBinomialConjugate

from survey.utils.plots import label_pair_bar_plot_pcts


class SingleCategoryMixin(object):

    name: str
    _data: Series
    data: Series
    _ordered: bool
    _categories: List[str]
    category_names: List[str]
    text: str

    def make_features(self, data: Optional[Series] = None,
                      drop_na: bool = True, null_value: str = None,
                      naming: str = '{{name}}: {{choice}}',
                      binarize: bool = True) -> Union[DataFrame, Series]:
        """
        Create DataFrame of binarized features for use in ML.

        :param data: Answers to the Question from a Survey.
        :param drop_na: Whether to drop rows from respondents that did not
                        answer the question.
        :param null_value: Optional "None of the above" type value to drop from
                           features.
        :param naming: Pattern to use to name the columns.
        :param binarize: Whether to split the results into separate columns.
        """
        if data is None:
            data = self._data
        if drop_na:
            data = data.dropna()
        if binarize:
            if not self._ordered:
                used_categories = [c for c in self._categories
                                   if c in data.unique().tolist()]
                features = get_dummies(data)[used_categories]
                if null_value is not None:
                    features = features.drop(null_value, axis=1)
                features.columns = [
                    naming.replace('{{name}}', self.name).replace(
                        '{{choice}}', choice
                    )
                    for choice in features.columns
                ]
            else:
                features = data.replace({
                    category: self._categories.index(category)
                    for category in self._categories
                })
        else:
            if null_value is not None:
                data = data.replace(null_value, nan)
            data = data.dropna()
            features = data.map(lambda x: self._categories.index(x))
        return features

    def correlation(self, other: 'SingleCategoryMixin') -> float:
        """
        Return the Spearman rank correlation coefficient of this Categorical
        with another.

        :param other: The other SingleCategory.
        """
        if not (self._ordered and other._ordered):
            raise ValueError("Can't calculate Rank Correlation Coefficient "
                             "for Unordered Categories")
        if isinstance(other, SingleCategoryMixin):
            other_features = other.make_features(binarize=False)
        else:
            other_features = other.make_features()
        return self.make_features(binarize=False).corr(other_features,
                                                       method='spearman')

    def plot_comparison(self, other: 'SingleCategoryMixin',
                        transpose: bool = False,
                        self_color: str = 'C0', other_color: str = 'C1',
                        significance: bool = False,
                        sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                        pct_size: Optional[int] = None,
                        ax: Optional[Axes] = None,
                        title: Optional[str] = None,
                        grid: bool = False,
                        max_axis_label_chars: Optional[int] = None,
                        x_label: Optional[str] = None,
                        y_lim: Optional[Tuple[int, int]] = None) -> Axes:
        """
        Plot a comparison between this and another SingleCategoryMixin.

        :param other: The other MultiChoiceQuestion to compare with.
        :param transpose: Whether to transpose the plot.
        :param self_color: The plot color for this question.
        :param other_color: The plot color for the other question.
        :param significance: Whether to calculate and show significant values.
        :param sig_colors: Pair of colors for high and low significant values.
        :param pct_size: Font size for the percentage labels.
        :param ax: Optional matplotlib axes to plot on.
        :param title: Optional title for the plot.
        :param grid: Whether to show a plot grid or not.
        :param max_axis_label_chars: Maximum number of characters in axis labels
                                     before wrapping.
        :param x_label: Label for the x-axis.
        :param y_lim: Optional limits for the y-axis.
        """
        ax = ax or new_axes()
        if self.name == other.name:
            raise ValueError(
                'Names of questions must be different to plot a comparison.'
            )
        self_counts = self.data.value_counts().rename(self.name)
        other_counts = other.data.value_counts().rename(other.name)
        plot_data = concat([
            self_counts, other_counts
        ], axis=1).reindex(self.category_names)
        plot_data.index = wrap_text(plot_data.index,
                                    max_width=max_axis_label_chars)
        if transpose:
            kind = 'barh'
        else:
            kind = 'bar'
        plot_data.plot(kind=kind, ax=ax, color=[self_color, other_color])
        if transpose:
            ax.set_xlabel('# Respondents')
        else:
            ax.set_ylabel('# Respondents')
        label_pair_bar_plot_pcts(
            item_counts=plot_data,
            item_pcts=100 * plot_data.fillna(0) / plot_data.sum(),
            ax=ax, transpose=transpose, font_size=pct_size
        )

        if significance:
            sig = self > other
            for c, category in enumerate(self.category_names):
                bar_1: Patch = ax.patches[c]
                bar_2: Patch = ax.patches[c + len(self.category_names)]
                if sig[category] >= 0.945:
                    bar_1.set_edgecolor(sig_colors[0])
                    bar_1.set_linewidth(2)
                    bar_2.set_edgecolor(sig_colors[1])
                    bar_2.set_linewidth(2)
                elif sig[category] < 0.055:
                    bar_1.set_edgecolor(sig_colors[1])
                    bar_1.set_linewidth(2)
                    bar_2.set_edgecolor(sig_colors[0])
                    bar_2.set_linewidth(2)

        if title is not None:
            ax.set_title(title)
        else:
            ax.set_title(self.text)
        if x_label is not None:
            ax.set_xlabel(x_label)
        if grid:
            ax.grid(True)
            ax.set_axisbelow(True)
        if y_lim is not None:
            ax.set_ylim(y_lim)

        return ax

    def count(self, values: Optional[Union[str, List[str]]] = None) -> int:
        """
        Return a count of the total number of responses matching the given value
        or values.

        :param values: A response value or list of values to match. Leave as
                       None to count all responses.
        """
        if values is None:
            return len(self._data.dropna())
        elif isinstance(values, str):
            values = [values]
        return len(self._data.loc[self._data.isin(values)])

    def counts(self, values: Optional[Union[str, List[str]]] = None) -> Series:
        """
        Return counts of number of responses matching each value in values.

        :param values: A response value or list of values to count instances of.
        """
        if values is None:
            values = self.category_names
        elif isinstance(values, str):
            values = [values]
        counts = self._data.value_counts()
        return Series(
            index=values,
            data=[counts[value] if value in counts.keys()
                  else 0
                  for value in values],
            name=self.name
        )

    def replace(self, replacements: Dict[str, str], categories: List[str],
                **kwargs) -> 'SingleCategoryMixin':
        """
        Replace categories with new ones
        e.g. for grouping similar responses {'apple': 'fruit',
                                             'orange': 'fruit',
                                             'potato': 'vegetable'}

        :param replacements: Dictionary of replacement values.
        :param categories: List of categories for the new item.
        :param kwargs: Other values required to create the new Categorical item.
        :return: New question or attribute.
        """
        data: Series = self.data
        data = data.replace(replacements)
        if 'name' not in kwargs.keys():
            kwargs['name'] = self.name
        if 'text' not in kwargs.keys():
            kwargs['text'] = self.name
        if 'ordered' not in kwargs.keys():
            kwargs['ordered'] = self._ordered
        new_item = type(self)(data=data, categories=categories, **kwargs)
        new_item.survey = self.survey
        return new_item

    def __gt__(self, other: 'SingleCategoryMixin') -> Series:
        """
        Return the probability that each response is selected in this question
        at a significantly higher rate than the other question.
        """
        results = []
        counts_self = self.data.value_counts()
        counts_other = other.data.value_counts()
        for category in self.category_names:
            n_self = counts_self.sum()
            try:
                m_self = counts_self[category]
            except KeyError:
                m_self = 0
            n_other = counts_other.sum()
            try:
                m_other = counts_other[category]
            except KeyError:
                m_other = 0
            results.append({
                'category': category,
                'p': (
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_self, k=m_self).posterior() >
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_other, k=m_other).posterior()
                )
            })
        results_data = DataFrame(results).set_index('category')['p']
        return results_data

    def __lt__(self, other: 'SingleCategoryMixin') -> Series:
        """
        Return the probability that each response is selected in this question
        at a significantly lower rate than the other question.
        """
        return other.__gt__(self)
