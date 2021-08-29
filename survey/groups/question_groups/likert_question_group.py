from collections import OrderedDict
from typing import Dict, Optional, List, Any, Tuple, Union

from matplotlib.figure import Figure
from mpl_format.axes.axes_formatter import AxesFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_format.figures.figure_formatter import FigureFormatter
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from pandas import Series, DataFrame, pivot_table, concat
from probability.distributions import BetaBinomialConjugate
from seaborn import heatmap

from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.question_container_mixin import \
    QuestionContainerMixin
from survey.mixins.containers.single_category_stack_mixin import \
    SingleCategoryStackMixin
from survey.mixins.containers.single_type_question_container_mixin import \
    SingleTypeQuestionContainerMixin
from survey.questions import LikertQuestion
from survey.utils.plots import draw_vertical_dividers
from survey.utils.type_detection import all_are


class LikertQuestionGroup(
    QuestionContainerMixin,
    SingleCategoryStackMixin,
    SingleTypeQuestionContainerMixin[LikertQuestion],
    CategoricalGroupMixin,
    object
):

    Q = LikertQuestion

    def __init__(self, questions: Dict[str, LikertQuestion] = None):

        if not all_are(questions.values(), LikertQuestion):
            raise TypeError('Not all attributes are LikertQuestions.')
        self._questions: List[LikertQuestion] = [q for q in questions.values()]
        self._set_categories()
        self._item_dict: Dict[str, LikertQuestion] = questions
        for property_name, question in questions.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property '
                      f'for Question: {question}')

    # region statistics

    def min(self) -> Series:
        return Series(OrderedDict([
            (key, question.min())
            for key, question in self._item_dict.items()
        ]))

    def max(self) -> Series:
        return Series(OrderedDict([
            (key, question.max())
            for key, question in self._item_dict.items()
        ]))

    def mean(self) -> Series:
        return Series(OrderedDict([
            (key, question.mean())
            for key, question in self._item_dict.items()
        ]))

    def median(self) -> Series:
        return Series(OrderedDict([
            (key, question.median())
            for key, question in self._item_dict.items()
        ]))

    def std(self) -> Series:
        return Series(OrderedDict([
            (key, question.std())
            for key, question in self._item_dict.items()
        ]))

    # endregion

    def significance_one_vs_any(self) -> Series:
        """
        Return the probability that the response to each question is higher than
        a randomly selected other question.
        """
        keys = list(self._item_dict.keys())
        results = []
        for key in keys:
            other_keys = [k for k in keys if k != key]
            data_one = self._item_dict[key].make_features()
            data_rest = concat([
                self._item_dict[k].make_features()
                for k in other_keys
            ], axis=0)
            bb_one = BetaBinomialConjugate(
                alpha=1, beta=1, n=len(data_one), k=data_one.sum()
            )
            bb_rest = BetaBinomialConjugate(
                alpha=1, beta=1, n=len(data_rest), k=data_rest.sum()
            )
            results.append({
                'name': key,
                'p': bb_one.posterior() > bb_rest.posterior()
            })
        results_data = DataFrame(results).set_index('name')['p']
        return results_data

    def significance_one_vs_one(self) -> DataFrame:
        """
        Return probability that the average response to each question in this
        group is higher than to each other question in this group.
        """
        return self >> self

    def __gt__(self, other: 'LikertQuestionGroup') -> Series:
        """
        Return probability that the average response to each question in this
        group is greater than the corresponding question in the other group.
        """
        if set(self._item_dict.keys()) != set(other._item_dict.keys()):
            raise ValueError(
                'Keys must be the same to compare LikertQuestionGroups'
            )
        results = []
        for key in self._item_dict.keys():
            results.append({
                'name': key,
                'p': self._item_dict[key] > other._item_dict[key]
            })
        return DataFrame(results).set_index('name')['p']

    def __lt__(self, other: 'LikertQuestionGroup') -> Series:
        """
        Return probability that the average response to each question in this
        group is less than the corresponding question in the other group.
        """
        return other.__gt__(self)

    def __rshift__(self, other: 'LikertQuestionGroup') -> DataFrame:
        """
        Return probability that the average response to each question in this
        group is higher than to each question in the other group.
        """
        results = []
        for key_self, question_self in self._item_dict.items():
            for key_other, question_other in other._item_dict.items():
                results.append({
                    'name_1': key_self,
                    'name_2': key_other,
                    'p': question_self > question_other
                })
        pt = pivot_table(data=DataFrame(results),
                         index='name_1', columns='name_2',
                         values='p')
        return pt

    def __lshift__(self, other: 'LikertQuestionGroup') -> DataFrame:
        """
        Return probability that the average response to each question in this
        group is less than the average response to each question in the other
        group.
        """
        return other.__rshift__(self)

    def merge_with(
            self, other: 'LikertQuestionGroup'
    ) -> 'LikertQuestionGroup':
        """
        Merge the questions in this group with those in the other.

        :param other: The other group to merge questions with.
        """
        if set(self.keys) != set(other.keys):
            raise KeyError('Keys must be identical '
                           'to merge LikertQuestionGroups')
        return LikertQuestionGroup({
            k: self[k].merge_with(other[k])
            for k in self.keys
        })

    def plot_comparison(self, ax: Axes = None, **kwargs) -> Axes:
        """
        Plot a comparison between the different question ratings.

        :param ax: Optional matplotlib axes.
        """
        ax = ax or new_axes()
        if 'cmap' not in kwargs:
            kwargs['cmap'] = 'Blues'
        data = DataFrame({k: q.value_counts()
                          for k, q in self.item_dict.items()})
        heatmap(data=data, ax=ax, annot=True, fmt='d', **kwargs)
        AxesFormatter(ax).set_text(
            x_label='Question', y_label='Rating'
        ).invert_y_axis()
        draw_vertical_dividers(ax)
        return ax

    def plot_distribution_grid(
            self, n_rows: int, n_cols: int,
            fig_size: Optional[Tuple[int, int]] = (16, 9),
            filters: Optional[Dict[str, Any]] = None,
            titles: Union[str, List[str], Dict[str, str]] = '',
            x_labels: Union[str, List[str], Dict[str, str]] = '',
            drop: Optional[Union[str, List[str]]] = None,
            group_significance: bool = False,
            group_sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
            **kwargs
    ) -> Figure:
        """
        Plot a grid of distributions of the group's questions.

        :param n_rows: Number of rows in the grid.
        :param n_cols: Number of columns in the grid.
        :param fig_size: Size for the figure.
        :param filters: Optional filters to apply to each question before
                        plotting.
        :param titles: List of titles or dict mapping question keys or names to
                       titles.
        :param x_labels: List of x-axis labels or dict mapping question keys or
                         names to labels.
        :param drop: Optional category or categories to exclude from the plot.
        :param group_significance: Whether to highlight the distributions which
                                   have significantly higher and lower values
                                   than others.
        :param group_sig_colors: Pair of colors for high and low significant
                                 values.
        :param kwargs: Other kwargs to pass to each question's
                       plot_distribution() method.
        """
        fig = super().plot_distribution_grid(
            n_rows=n_rows, n_cols=n_cols, fig_size=fig_size,
            filters=filters, titles=titles, x_labels=x_labels,
            drop=drop, **kwargs
        )
        ff = FigureFormatter(fig)
        if group_significance:
            significance = self.significance_one_vs_any()
            keys = list(significance.keys())
            for key, axf in zip(keys, ff.multi.flat):
                if significance[key] >= 0.945:
                    axf.set_frame_color(group_sig_colors[0])
                elif significance[key] < 0.055:
                    axf.set_frame_color(group_sig_colors[1])
        return fig

    def value_counts(self) -> Optional[DataFrame]:
        """
        Return a dataframe of counts of responses for each category for each
        question in the group.

        Returns `None` if all questions do not share the same categories.
        """
        if self.categories is None:
            return None
        category_order = list(self.categories.keys())
        records = []
        for key, question in self._item_dict.items():
            record = {
                'key': key,
                'text': question.text,
                'name': question.name
            }
            record = {**record, **question.value_counts().to_dict()}
            records.append(record)
        data = DataFrame(records)
        data = data.set_index(['key', 'text', 'name']).fillna(0).astype(int)
        data = data.reindex(columns=category_order)

        return data
