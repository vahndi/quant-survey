from collections import OrderedDict
from itertools import product
from typing import Dict, List, Union, Callable, Optional, Tuple

from matplotlib.axes import Axes
from matplotlib.patches import Patch
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text
from pandas import Series, DataFrame, pivot_table, concat
from probability.distributions import BetaBinomialConjugate

from survey.mixins.data_mixins import SingleCategoryDataMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.single_category_distribution_mixin import \
    SingleCategoryDistributionMixin
from survey.mixins.data_types.single_category_pt_mixin import \
    SingleCategoryPTMixin
from survey.mixins.data_types.single_category_significance_mixin import \
    SingleCategorySignificanceMixin
from survey.mixins.data_validation.single_category_validation_mixin import \
    SingleCategoryValidationMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question
from survey.utils.formatting import trim_common_leading, find_common_leading, \
    trim_common_trailing
from survey.utils.plots import plot_categorical_distributions, \
    label_pair_bar_plot_pcts


class LikertQuestion(
    NamedMixin,
    SingleCategoryDataMixin,
    CategoricalMixin,
    SingleCategoryDistributionMixin,
    SingleCategorySignificanceMixin,
    SingleCategoryValidationMixin,
    SingleCategoryPTMixin,
    Question
):
    """
    Class to represent a Survey Question with responses on a Likert scale.
    Choices must either be or begin with a number
    e.g. `"1 - strongly disagree"`, "1" or 1
    """
    def __init__(self, name: str, text: str,
                 categories: Dict[str, int],
                 data: Optional[Series] = None):
        """
        Create a new Likert-scale question.

        :param name: A pythonic name for the question.
        :param text: The text asked in the question.
        :param categories: The dict of possible choices, mapping name -> value.
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        # add choices sorted ascending by value
        val_to_name = {int_val: str_name
                       for str_name, int_val in categories.items()}
        self._set_categories(OrderedDict([
            (val_to_name[val], val)
            for val in sorted(val_to_name.keys())
        ]))
        if data is not None:
            data = data.astype('category')
        self.data = data
        self._ordered = True

    def _validate_data(self, data: Series):

        errors = []
        for unique_val in data.dropna().unique():
            if unique_val not in self.category_names:
                errors.append(
                    f'"{unique_val}" is not in categories for "{self.name}".'
                )
        if errors:
            raise ValueError('\n'.join(errors))

    def make_features(self, answers: Series = None,
                      normalize: Union[Dict[float, float], bool] = True,
                      norm_min: float = 0.0, norm_max: float = 1.0,
                      drop_na: bool = True) -> Series:
        """
        Create DataFrame of features for use in ML.

        :param answers: Answers to the Question from a Survey.
        :param normalize: Option to normalize the data by min-max normalization
                          or map using a dictionary.
        :param norm_min: Value to use for lower bound of normalization range.
        :param norm_max: Value to use for upper bound of normalization range.
        :param drop_na: Whether to drop null responses from returned features.
        """
        if answers is None:
            answers = self._data
        if drop_na:
            answers = answers.dropna()
        features = Series(
            data=answers.replace(self._categories),
            index=answers.index
        )
        if type(normalize) is bool:
            if normalize:
                min_cat_val = min(self.categories.values())
                max_cat_val = max(self.categories.values())
                return (
                    norm_min +
                    (features - min_cat_val) *
                    (norm_max - norm_min) /
                    (max_cat_val - min_cat_val)
                )
            else:
                return features
        elif isinstance(normalize, dict):
            return features.map(normalize)
        else:
            raise TypeError('normalize needs to be either bool or dictionary')

    def significance_one_vs_one(self) -> DataFrame:
        """
        Return the probability that a random respondent is more likely to answer
        each category than each other.
        """
        results = []
        for category_1, category_2 in product(self._categories,
                                              self._categories):
            try:
                category_1_count = self._data.value_counts()[category_1]
            except KeyError:
                category_1_count = 0
            try:
                category_2_count = self._data.value_counts()[category_2]
            except KeyError:
                category_2_count = 0
            num_responses = len(self._data.dropna())
            bb_category_1 = BetaBinomialConjugate(
                alpha=1, beta=1, n=num_responses, k=category_1_count
            )
            bb_category_2 = BetaBinomialConjugate(
                alpha=1, beta=1, n=num_responses, k=category_2_count
            )
            results.append({
                'category_1': category_1,
                'category_2': category_2,
                'p': bb_category_1.posterior() > bb_category_2.posterior()
            })

        results_data = DataFrame(results)
        pt = pivot_table(data=results_data,
                         index='category_1', columns='category_2',
                         values='p')
        return pt

    def plot_comparison(self, other: 'LikertQuestion',
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
                if sig >= 0.945:
                    bar_1.set_edgecolor(sig_colors[0])
                    bar_1.set_linewidth(2)
                    bar_2.set_edgecolor(sig_colors[1])
                    bar_2.set_linewidth(2)
                elif sig < 0.055:
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

    @staticmethod
    def plot_distributions(questions: List['LikertQuestion'],
                           order: Optional[List[str]] = None,
                           sort_by: Union[str, Callable, list] = None,
                           ax: Optional[Axes] = None) -> Axes:
        """
        Plot a stacked bar chart of Likert values for each question.

        :param questions: Questions to plot distributions of
        :param order: Optional ordering for the Likert values
        :param sort_by: Column name(s) and/or lambda function(s) to sort by,
                        e.g. lambda d: d['1'] + d['2']
        :param ax: Optional matplotlib axes to plot on
        """
        data = [question.data for question in questions]
        texts = [question.text for question in questions]
        common_leading = find_common_leading(texts)
        texts = trim_common_leading(texts)
        texts = trim_common_trailing(texts)
        for q, question in enumerate(questions):
            data[q].name = texts[q]
        ax = ax or new_axes()
        ax = plot_categorical_distributions(
            data=data, order=order, sort_by=sort_by, ax=ax
        )
        if common_leading:
            ax.set_title(common_leading)
        ax.set_ylabel('# Respondents')
        return ax

    def merge_with(self, other: 'LikertQuestion', **kwargs) -> 'LikertQuestion':
        """
        Merge the answers to this question with the other.

        :param other: The other question to merge answers with.
        :param kwargs: Initialization parameters for new question.
                       Use self values if not given.
        """
        if self.categories != other.categories:
            raise ValueError('Categories must be identical to merge questions.')
        kwargs['data'] = self._get_merge_data(other)
        kwargs = self._update_init_dict(kwargs, 'name', 'text', 'categories')
        new_question = LikertQuestion(**kwargs)
        new_question.survey = self.survey
        return new_question

    def correlation(self, other: 'LikertQuestion') -> float:
        return self.make_features().corr(
            other.make_features(), method='spearman'
        )

    def min(self) -> float:
        return self.make_features(normalize=False).min()

    def max(self) -> float:
        return self.make_features(normalize=False).max()

    def mean(self) -> float:
        return self.make_features(normalize=False).mean()

    def median(self) -> float:
        return self.make_features(normalize=False).median()

    def std(self) -> float:
        return self.make_features(normalize=False).std()

    def stack(self, other: 'LikertQuestion',
              name: Optional[str] = None,
              text: Optional[str] = None) -> 'LikertQuestion':

        if self.data.index.names != other.data.index.names:
            raise ValueError('Indexes must have the same names.')
        if set(self.categories) != set(other.categories):
            raise ValueError('Questions must have the same categories.')
        new_data = concat([self.data, other.data])
        new_question = LikertQuestion(
            name=name or self.name, text=text or self.text,
            categories=self.categories,
            data=new_data
        )
        new_question.survey = self.survey
        return new_question

    def count(
            self,
            values: Optional[Union[str, List[str]]] = None
    ) -> int:
        """
        Return a count of the total number of responses matching the given value
        or values.

        :param values: A response value or list of values to match.
                       Leave as None to count all responses.
        """
        if values is None:
            return len(self._data.dropna())
        elif isinstance(values, str):
            values = [values]
        return len(self._data.loc[self._data.isin(values)])

    def value_counts(
            self,
            values: Optional[Union[str, List[str]]] = None
    ) -> Series:
        """
        Return counts of number of responses matching each value in the given
        value or values.

        :param values: A response value or list of values to count instances of.
        """
        if values is None:
            values = self.category_names
        if not isinstance(values, list):
            values = [values]
        counts = self._data.value_counts()
        return Series(
            index=values,
            data=[counts[value] if value in counts.keys() else 0
                  for value in values],
            name=self.name
        )

    def __gt__(self, other: 'LikertQuestion') -> float:
        """
        Return the probability that the posterior estimate for the probability
        of max-rating is greater in self than other.
        """
        data_self = self.make_features()
        data_other = other.make_features()
        bb_self = BetaBinomialConjugate(
            alpha=1, beta=1, n=len(data_self), k=data_self.sum()
        )
        bb_other = BetaBinomialConjugate(
            alpha=1, beta=1, n=len(data_other), k=data_other.sum()
        )
        return bb_self.posterior() > bb_other.posterior()

    def __lt__(self, other: 'LikertQuestion') -> float:
        """
        Return the probability that the posterior estimate for the probability
        of max-rating is greater in other than self.
        """
        return other > self

    def __getitem__(self, item: Union[str, List[str]]) -> 'LikertQuestion':
        """
        Return a new LikertQuestion with a subset of the items in the
        categories.

        :param item: Item or items to use to filter the data.
        """
        if isinstance(item, str):
            categories = [item]
        else:
            categories = item
        if not set(categories).issubset(self.category_names):
            raise ValueError('Item to get must be subset of categories.')
        new_data = self._data.loc[self._data.isin(categories)]
        return LikertQuestion(
            name=self.name, text=self.text,
            categories=OrderedDict([(k, v) for k, v in self._categories.items()
                                    if k in categories]),
            data=new_data
        )

    def __repr__(self):

        choices = ', '.join(
            f"'{name}': {value}"
            for name, value in self.categories.items()
        )
        return (
            f"LikertQuestion("
            f"\n\tname='{self.name}',"
            f"\n\tchoices={choices}"
            f"\n)"
        )

