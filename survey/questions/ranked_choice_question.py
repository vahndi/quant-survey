from itertools import product
from typing import List, Optional, Dict, Tuple

from matplotlib.axes import Axes
from mpl_format.axes.axes_formatter import AxesFormatter
from mpl_format.text.text_utils import map_text, wrap_text
from pandas import Series, isnull, DataFrame, pivot_table, notnull
from probability.distributions import BetaBinomialConjugate
from seaborn import heatmap

from survey.constants import CATEGORY_SPLITTER
from survey.mixins.data_mixins import MultiCategoryDataMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question
from survey.utils.plots import draw_vertical_dividers, draw_horizontal_dividers


class RankedChoiceQuestion(
    NamedMixin,
    MultiCategoryDataMixin,
    CategoricalMixin,
    Question
):
    """
    A question where Respondents are asked to rank various choices in order of
    preference.
    e.g. for 10 items 1 is the most favourite and 10 is the least favourite.
    """
    def __init__(self, name: str, text: str, categories: List[str],
                 data: Optional[Series] = None):
        """
        Create a new Ranked Choice question.

        :param name: A pythonic name for the question.
        :param text: The text asked in the question.
        :param categories: The list of possible choices.
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        self._set_categories(categories)
        self.data = data

    def _validate_data(self, data: Series):
        unique = set([selection for ix, item in data.iteritems()
                     for selection in item.split(CATEGORY_SPLITTER)
                     if notnull(selection)])
        errors = []
        for unique_val in unique:
            if unique_val not in self._categories:
                errors.append(f'"{unique_val}" is not in categories.')
        if errors:
            raise ValueError('\n'.join(errors))

    def make_features(self, answers: Series = None,
                      drop_na: bool = True,
                      naming: str = '{{name}}: {{choice}}',
                      normalize: bool = True) -> DataFrame:
        """
        Create DataFrame of features for use in ML.

        :param answers: Answers to the Question from a Survey. If left as None
                        then use the Question's attached data.
        :param drop_na: Whether to drop null rows (rows where respondent was not
                        asked a question).
        :param naming: Pattern to use to name the columns.
        :param normalize: Option to normalize data with min and max approach.
        """
        if answers is None:
            answers = self._data
        if drop_na:
            # drop respondents that weren't asked the question
            answers = answers.dropna()
        feature_list = []
        if len(answers) > 0:
            # create features
            for _, str_selections in answers.iteritems():
                feature_dict = {}
                selections = str_selections.split(CATEGORY_SPLITTER)
                for i in range(len(selections)):
                    feature_dict.update({selections[i]: i + 1})
                feature_list.append(feature_dict)
            features = DataFrame(data=feature_list, index=answers.index,
                                 columns=self.categories)
        else:
            # create empty dataframe with the right columns
            features = DataFrame(columns=self.categories, index=answers.index)
        # rename columns
        features.columns = [
            naming.replace('{{name}}', self.name)
                  .replace('{{choice}}', choice)
            for choice in features.columns
        ]
        # normalize
        if normalize:
            features = (
                (features - features.min()) /
                (features.max() - features.min())
            )
        else:
            # set datatype
            features = features.astype(int)

        return features

    def significance__one_vs_any(self) -> Series:
        """
        Return the probability that one choice is ranked higher than a randomly
        selected other choice.
        """
        data = self.make_features(naming='{{choice}}')
        sums: Series = data.sum()
        n = len(data)
        results = []
        for category in self.categories:
            rest = [c for c in self.categories if c != category]
            m_one = sums[category]
            m_rest = sums[rest].mean()
            results.append({
                'category': category,
                'p': (
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n, k=m_one).posterior() >
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n, k=m_rest).posterior()
                )
            })
        return DataFrame(results).set_index('category')['p']

    def significance_one_vs_one(self) -> DataFrame:
        """
        Return the probability that each choice is ranked higher than each
        other.
        """
        data = self.make_features(naming='{{choice}}')
        sums: Series = data.sum()
        n = len(data)
        results = []
        for category_1, category_2 in product(self.categories, self.categories):
            m_1 = sums[category_1]
            m_2 = sums[category_2]
            results.append({
                'category_1': category_1,
                'category_2': category_2,
                'p': (
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n, k=m_1).posterior() >
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n, k=m_2).posterior()
                )
            })
        results_data = DataFrame(results)
        pt = pivot_table(data=results_data,
                         index='category_1', columns='category_2',
                         values='p')
        return pt

    def plot_distribution(self, data: Optional[Series] = None,
                          transpose: bool = False,
                          normalize: bool = False,
                          significance: bool = False,
                          sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                          sig_values: Tuple[float, float] = (0.945, 0.055),
                          label_mappings: Optional[Dict[str, str]] = None,
                          ax: Optional[Axes] = None) -> Axes:
        """
        Plot the distribution of answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param transpose: Whether to transpose the labels to the y-axis.
        :param normalize: Whether to normalize number of responses in each
                          position to total number of responses.
        :param significance: Whether to highlight significant choices.
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
        :param sig_values: Tuple of (high, low) values for assessing
                           significance.
        :param label_mappings: Optional dict of replacements for labels.
        :param ax: Optional matplotlib axes to plot on.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        order_counts = []
        for index, str_user_order in data.iteritems():
            if isnull(str_user_order):
                continue
            user_order = str_user_order.split(CATEGORY_SPLITTER)
            for i in range(len(user_order)):
                order_counts.append({
                    'choice': user_order[i],
                    'rank': i + 1,
                })
        counts = DataFrame(order_counts).groupby([
            'choice', 'rank'
        ]).size().reset_index().rename(columns={0: 'count'})
        pivot = pivot_table(
            data=counts, index='choice',
            columns='rank', values='count'
        ).reindex(self.categories)
        pivot.index = wrap_text(map_text(pivot.index,
                                         mapping=label_mappings or {}))
        if normalize:
            fmt = '.2f'
            pivot = pivot / len(data)
        else:
            fmt = '.0f'
        if transpose:
            pivot = pivot.T
        axf = AxesFormatter(axes=ax)
        ax = axf.axes
        heatmap(data=pivot, annot=True, fmt=fmt, cmap='Blues', ax=ax)

        if significance:
            cat_sigs = self.significance__one_vs_any()
            for category, sig_value in cat_sigs.iteritems():
                if sig_values[1] < sig_value < sig_values[0]:
                    continue
                elif sig_value <= sig_values[1]:
                    color = sig_colors[1]
                elif sig_value >= sig_values[0]:
                    color = sig_colors[0]
                if not transpose:
                    x_min = 0.1
                    x_max = len(self.categories) - 0.1
                    y_min = self.categories.index(category) + 0.1
                    y_max = self.categories.index(category) + 0.9
                else:
                    y_min = 0.1
                    y_max = len(self.categories) - 0.1
                    x_min = self.categories.index(category) + 0.1
                    x_max = self.categories.index(category) + 0.9
                ax.plot(
                    [x_min, x_max, x_max, x_min, x_min],
                    [y_min, y_min, y_max, y_max, y_min],
                    color=color, linewidth=2
                )

        axf.x_axis.tick_labels.set_ha_center()
        axf.y_axis.tick_labels.set_va_center()
        if transpose:
            draw_vertical_dividers(ax)
        else:
            draw_horizontal_dividers(ax)
        axf.set_title_text(self.text)
        return ax

    def distribution_table(self, data: Optional[Series] = None,
                           significance: bool = False) -> DataFrame:
        """
        Create a table of the distribution of responses.

        :param data: The answers given by Respondents to the Question.
        :param significance: Whether to calculate significance for the
                             responses.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        order_counts = []
        for index, str_user_order in data.iteritems():
            if isnull(str_user_order):
                continue
            user_order = str_user_order.split(CATEGORY_SPLITTER)
            for i in range(len(user_order)):
                order_counts.append({
                    'Choice': user_order[i],
                    'Rank': i + 1,
                })
        counts = DataFrame(order_counts).groupby([
            'Choice', 'Rank'
        ]).size().reset_index().rename(columns={0: 'Count'})
        pivot = pivot_table(
            data=counts, index='Choice',
            columns='Rank', values='Count'
        ).reindex(self.categories)

        if significance:
            pivot['Significance'] = self.significance__one_vs_any()

        return pivot

    def __repr__(self):

        choices = ', '.join(f"'{choice}'" for choice in self._categories)
        return (
            f"RankedChoiceQuestion(\n"
            f"\tname='{self.name}',\n"
            f"\tchoices=[{choices}]\n"
            f")"
        )
