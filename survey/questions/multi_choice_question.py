from itertools import product
from typing import List, Optional, Dict, Tuple, Union, TYPE_CHECKING

from matplotlib.axes import Axes
from matplotlib.patches import Patch
from mpl_format.axes.axes_formatter import AxesFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text, map_text
from numpy import nan
from pandas import Series, DataFrame, pivot_table, concat, isnull, notnull
from probability.distributions import BetaBinomialConjugate

from survey.constants import CATEGORY_SPLITTER
from survey.mixins.data_mixins import MultiCategoryDataMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.data_types.multi_category_pt_mixin import \
    MultiCategoryPTMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question
from survey.utils.plots import label_bar_plot_pcts, label_pair_bar_plot_pcts

if TYPE_CHECKING:
    from survey.questions import SingleChoiceQuestion


class MultiChoiceQuestion(
    NamedMixin,
    MultiCategoryDataMixin,
    CategoricalMixin,
    MultiCategoryPTMixin,
    Question
):
    """
    Class to represent a Survey Question where the Respondent can choose one or
    more options from at least two.
    """
    def __init__(self, name: str, text: str, categories: List[str],
                 ordered: bool, data: Optional[Series] = None):
        """
        Create a new multiple choice question.

        :param name: A pythonic name for the question.
        :param text: The text asked in the question.
        :param categories: The list of possible choices.
        :param ordered: Whether the choices passed are ordered (low to high).
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        self._set_categories(categories)
        self.data = data
        self._ordered = ordered

    def _validate_data(self, data: Series):

        unique = set([selection for ix, item in data.dropna().iteritems()
                     for selection in item.split(CATEGORY_SPLITTER)
                     if notnull(selection)])
        errors = []
        error_vals = []
        for unique_val in unique:
            if unique_val not in self._categories:
                error_vals.append(unique_val)
                errors.append(f'"{unique_val}" is not in categories'
                              f' for question "{self.text}".')
        if errors:
            raise ValueError(
                '\n'.join(errors) +
                '\nList of values:\n' + '\n'.join(error_vals)
            )

    def make_features(self, answers: Series = None, drop_na: bool = True,
                      naming: str = '{{name}}: {{choice}}',
                      null_category: Optional[str] = None) -> DataFrame:
        """
        Create DataFrame of binarized features for use in ML.

        :param answers: Answers to the Question from a Survey. If left as None
                        then use the Question's attached data.
        :param drop_na: Whether to drop null rows (rows where respondent was not
                        asked a question).
        :param naming: Pattern to use to name the columns.
                       '{{name}}' will be substituted with the name of the
                       question.
                       '{{choice}}' will be substituted with the name of the
                       choice.
        :param null_category: Optional response to exclude from the features,
                              e.g. a "None of the above" type option.
        """
        if answers is None:
            answers = self._data
        # define categories
        if null_category is not None:
            categories = [c for c in self._categories if c != null_category]
        else:
            categories = self._categories
        if drop_na:
            # drop respondents that weren't asked the question
            answers = answers.dropna()
        feature_list = []
        if len(answers) > 0:
            # create features
            for _, str_selections in answers.iteritems():
                feature_dict = {}
                if isnull(str_selections):
                    feature_dict.update({choice: nan for choice in categories})
                else:
                    selections = str_selections.split(CATEGORY_SPLITTER)
                    feature_dict.update({
                        choice: choice in selections
                        for choice in categories
                    })
                feature_list.append(feature_dict)
            features = DataFrame(
                data=feature_list, index=answers.index, columns=categories
            )
        else:
            # create empty dataframe with the right columns
            features = DataFrame(columns=categories, index=answers.index)
        # rename columns
        features.columns = [
            naming.replace('{{name}}', self.name).replace('{{choice}}', choice)
            for choice in features.columns
        ]
        # set datatype
        try:
            features = features.astype(int)  # only works if no nans
        except ValueError:
            pass

        return features

    def significance_one_vs_any(self) -> Series:
        """
        Return the probability that a random respondent is more likely to answer
        one category than a randomly selected other category.
        """
        data = self.make_features(naming='{{choice}}')
        sums = data.sum()
        results = []
        for category in self.categories:
            rest = [c for c in self.categories if c != category]
            n_one = len(data)
            m_one = sums[category]
            n_rest = len(rest) * len(data)
            m_rest = sums[rest].sum()
            results.append({
                'category': category,
                'p': (
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_one, k=m_one).posterior() >
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_rest, k=m_rest).posterior()
                )
            })
        return DataFrame(results).set_index('category')['p']

    def significance_one_vs_one(self) -> DataFrame:
        """
        Return the probability that a random respondent is more likely to answer
        one category than each other.
        """
        data = self.make_features(naming='{{choice}}')
        n = len(data)
        sums = data.sum()
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
                          drop_na: bool = True,
                          transpose: bool = True,
                          color: str = 'C0', pct_size: int = None,
                          significance: bool = False,
                          sig_colors: Tuple[str, str] = ('#00ff00', '#ff0000'),
                          label_mappings: Optional[Dict[str, str]] = None,
                          grid: bool = False,
                          max_axis_label_chars: Optional[int] = None,
                          title: Optional[str] = None,
                          x_label: Optional[str] = None,
                          y_label: Optional[str] = None,
                          ax: Optional[Axes] = None,
                          **kwargs) -> Axes:
        """
        Plot the distribution of answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param drop_na: Whether to drop null responses from the dataset
                        (affects % calculations).
        :param transpose: Whether to transpose the labels to the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        :param color: Color or list of colors for the bars.
        :param pct_size: Font size for the percent markers.
        :param significance: Whether to highlight significant categories.
        :param sig_colors: Tuple of (high, low) colors for highlighting
                           significance.
        :param label_mappings: Optional dict of replacements for labels.
        :param grid: Whether to show a plot grid or not.
        :param max_axis_label_chars: Maximum number of characters in axis labels
                                     before wrapping.
        :param title: Axes title.
        :param x_label: Label for the x-axis.
        :param y_label: Label for the y-axis.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        if len(data) == 0:
            return ax
        if title is None:
            title = self.text
        if x_label is None:
            x_label = self.name if not transpose else '# Respondents'
        if y_label is None:
            y_label = '# Respondents' if not transpose else self.name
        features = self.make_features(
            answers=data, drop_na=drop_na, naming='{{choice}}'
        )
        item_counts: Series = features.sum()
        plot_type = 'barh' if transpose else 'bar'
        ax = ax or new_axes()
        if label_mappings is not None:
            item_counts.index = wrap_text(
                map_text(item_counts.index, mapping=label_mappings or {}),
                max_width=max_axis_label_chars
            )
        else:
            item_counts.index = wrap_text(
                item_counts.index,
                max_width=max_axis_label_chars
            )

        edge_color = None
        line_width = None
        if significance:
            one_vs_any = self.significance_one_vs_any()
            edge_color = [sig_colors[0] if one_vs_any[category] >= 0.945 else
                          sig_colors[1] if one_vs_any[category] < 0.055 else
                          color for category in self.category_names]
            line_width = [2 if ec != color else None for ec in edge_color]

        item_counts.plot(kind=plot_type, ax=ax, color=color,
                         edgecolor=edge_color, linewidth=line_width,
                         **kwargs)

        # add percentages
        item_pcts = 100 * item_counts.div(len(features))
        label_bar_plot_pcts(item_counts=item_counts, item_pcts=item_pcts,
                            ax=ax, transpose=transpose, font_size=pct_size)

        # add titles and grid
        AxesFormatter(ax).set_text(
            title=title, x_label=x_label, y_label=y_label
        ).set_axis_below(True).grid(grid)
        if transpose and not x_label:
            ax.set_xlabel('# Respondents')
        elif not transpose and not y_label:
            ax.set_ylabel('# Respondents')

        return ax

    def plot_comparison(self, other: 'MultiChoiceQuestion',
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
        Plot a comparison between this and another MultiChoiceQuestion.

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
        self_counts = self.make_features(
            naming='{{choice}}'
        ).sum().rename(self.name)
        other_counts = other.make_features(
            naming='{{choice}}'
        ).sum().rename(other.name)
        if self.name == other.name:
            raise ValueError(
                'Questions must have different names to plot a comparison.'
            )
        num_respondents = Series({
            self.name: len(self.data.dropna()),
            other.name: len(other.data.dropna())
        })
        plot_data = concat([
            self_counts, other_counts
        ], axis=1).reindex(self.category_names)
        plot_data.index = wrap_text(text=plot_data.index,
                                    max_width=max_axis_label_chars)
        if transpose:
            kind = 'barh'
        else:
            kind = 'bar'
        plot_data.plot(kind=kind, ax=ax,
                       color=[self_color, other_color])
        if transpose:
            ax.set_xlabel('# Respondents')
        else:
            ax.set_ylabel('# Respondents')
        label_pair_bar_plot_pcts(
            item_counts=plot_data,
            item_pcts=100 * plot_data.fillna(0) / num_respondents,
            ax=ax, transpose=transpose, font_size=pct_size
        )

        if significance:
            sig = self > other
            for c, category in enumerate(self.category_names):
                bar_1: Patch = ax.patches[c]
                bar_2: Patch = ax.patches[c + len(self.category_names)]
                if sig[category] >= 0.945:
                    bar_1.set_edgecolor(sig_colors[0])
                    bar_2.set_edgecolor(sig_colors[1])
                elif sig[category] < 0.055:
                    bar_1.set_edgecolor(sig_colors[1])
                    bar_2.set_edgecolor(sig_colors[0])

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

    def where(self, **kwargs) -> 'MultiChoiceQuestion':
        """
        Return a copy of the question with only the data where the survey
        matches the given arguments.
        e.g. to filter down to Males who answered 'Yes' to 'q1',
        use question.where(gender='Male', q1='Yes')

        See FilterableMixin.where() for further documentation.
        """
        return super().where(**kwargs)

    def replace(self, replacements: Dict[str, str], categories: List[str],
                **kwargs) -> 'MultiChoiceQuestion':
        """
        Replace categories with new ones e.g. for grouping similar responses
            {'apple': 'fruit',
             'orange': 'fruit',
             'potato': 'vegetable'}

        :param replacements: Dictionary of replacement values.
        :param categories: List of categories for the new item.
        :param kwargs: Other values required to create the new Categorical item.
        :return: New question or attribute.
        """
        data: Series = self.data

        def replace_item(item: str):
            if isnull(item):
                return nan
            items = item.split(CATEGORY_SPLITTER)
            items = [replacements[item] if item in replacements.keys()
                     else item for item in items]
            return CATEGORY_SPLITTER.join(items)

        data = data.map(replace_item)
        if 'name' not in kwargs.keys():
            kwargs['name'] = self.name
        if 'text' not in kwargs.keys():
            kwargs['text'] = self.name
        if 'ordered' not in kwargs.keys():
            kwargs['ordered'] = self._ordered

        new_question = type(self)(data=data, categories=categories, **kwargs)
        new_question.survey = self.survey
        return new_question

    def count(self, values: Optional[Union[str, List[str]]] = None,
              how: Optional[str] = 'any') -> int:
        """
        Return a count of the total number of responses matching values.

        :param values: A response value or list of values to match. Leave as
                       None to count all responses.
        :param how: Use 'any' to count every respondent who selects any of the
                    values, 'all' to count only those who select all given
                    values (those who select others not given will also be
                    counted).
        """
        features = self.make_features(naming='{{choice}}', drop_na=True)
        if values is None:
            return len(features)
        else:
            if isinstance(values, str):
                values = [values]
            match_dict = {value: 1 for value in values}
            if how == 'any':
                return len(features.loc[(
                        features[list(match_dict)] == Series(match_dict)
                ).any(axis=1)])
            elif how == 'all':
                return len(features.loc[(
                        features[list(match_dict)] == Series(match_dict)
                ).all(axis=1)])
            else:
                raise ValueError("`how` must be one of ['any', 'all']")

    def counts(self, values: Optional[Union[str, List[str]]] = None,
               how: Optional[str] = 'any') -> Series:
        """
        Return counts of the total number of responses matching any or all
        values.

        :param values: A response value or list of values to match. Leave as
                       None to count all responses.
        :param how: Use 'any' to count every respondent who selects any of the
                    values, 'all' to count only those who select all given
                    values (those who select others not given will also be
                    counted).
        """
        features = self.make_features(naming='{{choice}}', drop_na=True)
        if values is None:
            return features.sum()
        else:
            if isinstance(values, str):
                values = [values]
            match_dict = {value: 1 for value in values}
            if how == 'any':
                matches = features.loc[(
                        features[list(match_dict)] == Series(match_dict)
                ).any(axis=1)]
                return matches.sum()
            elif how == 'all':
                matches = features.loc[(
                        features[list(match_dict)] == Series(match_dict)
                ).all(axis=1)]
                return matches.sum()
            else:
                raise ValueError("`how` must be one of ['any', 'all']")

    def merge_with(
            self, other: 'MultiChoiceQuestion', **kwargs
    ) -> 'MultiChoiceQuestion':
        """
        Merge the answers to this question with the other.

        :param other: The other question to merge answers with.
        :param kwargs: Initialization parameters for new question.
                       Use self values if not given.
        """
        if self.categories != other.categories:
            raise ValueError('Categories must be identical to merge questions.')
        kwargs['data'] = self._get_merge_data(other)
        kwargs = self._update_init_dict(
            kwargs, 'name', 'text', 'categories', 'ordered'
        )
        new_question = MultiChoiceQuestion(**kwargs)
        new_question.survey = self.survey
        return new_question

    def num_selections(self) -> Series:
        """
        Return the number of selections made by each respondent.
        """
        return self.make_features().sum(axis=1)

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
        features = self.make_features(
            answers=data, drop_na=True, naming='{{choice}}'
        )
        item_counts: Series = features.sum()
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

    def stack(self, other: 'MultiChoiceQuestion',
              name: Optional[str] = None,
              text: Optional[str] = None) -> 'MultiChoiceQuestion':

        if self.data.index.names != other.data.index.names:
            raise ValueError('Indexes must have the same names.')
        if set(self.categories) != set(other.categories):
            raise ValueError('Questions must have the same categories.')
        new_data = concat([self.data, other.data])
        new_question = MultiChoiceQuestion(
            name=name or self.name, text=text or self.text,
            categories=self.categories,
            ordered=self._ordered,
            data=new_data
        )
        new_question.survey = self.survey
        return new_question

    def __gt__(self, other: 'MultiChoiceQuestion') -> Series:

        self_data = self.make_features(naming='{{choice}}')
        other_data = other.make_features(naming='{{choice}}')
        n_self = self_data.shape[0]
        n_other = other_data.shape[0]
        results = []
        for category in self.category_names:
            m_self = self_data[category].sum()
            m_other = other_data[category].sum()
            results.append({
                'category': category,
                'p': (
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_self, k=m_self).posterior() >
                    BetaBinomialConjugate(
                        alpha=1, beta=1, n=n_other, k=m_other).posterior()
                )
            })
        return DataFrame(results).set_index('category')['p']

    def __lt__(self, other: 'MultiChoiceQuestion') -> Series:

        return other > self

    def __getitem__(
            self, item: str, yes_no: List[str] = None
    ) -> 'SingleChoiceQuestion':
        """
        Return a new SingleChoiceQuestion using a single category of the
        question.

        :param item: Name of the item to return in the new SingleChoiceQuestion.
        :param yes_no: List of 2 strings to map selected and not-select values
                       to. Defaults to ['Yes', 'No'].
        :rtype: SingleChoiceQuestion
        """
        yes_no = yes_no or ['Yes', 'No']
        if item not in self.categories:
            raise ValueError(f'{item} does not exist in {self.name}')
        bool_data = self.make_features(
            drop_na=False, naming='{{choice}}'
        )[item].replace({
            nan: nan, 1: yes_no[1], 0: yes_no[0]
        })
        from survey.questions import SingleChoiceQuestion
        return SingleChoiceQuestion(
            name=item, text=self.text,
            categories=['Yes', 'No'], ordered=True,
            data=bool_data
        )

    def __repr__(self):

        str_choices = ', '.join(f"'{choice}'" for choice in self._categories)
        return (
            f"MultiChoiceQuestion(\n"
            f"\tname='{self.name}',\n"
            f"\tchoices=[{str_choices}]\n"
            f")"
        )

