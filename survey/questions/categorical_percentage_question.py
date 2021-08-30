from typing import List, Optional, Dict

from matplotlib.axes import Axes
from numpy import sum
from pandas import Series, DataFrame, isnull

from survey.mixins.data_mixins import ObjectDataMixin
from survey.mixins.data_types.categorical_mixin import CategoricalMixin
from survey.mixins.named import NamedMixin
from survey.questions import Question


class CategoricalPercentageQuestion(
    NamedMixin,
    ObjectDataMixin,
    CategoricalMixin,
    Question
):
    """
    Class to represent a Survey Question where the Respondent is asked to
    assign a percentage to a number of Categorical items, totalling a maximum
    of 100%.
    """
    def __init__(self, name: str, text: str, categories: List[str],
                 data: Optional[Series] = None):
        """
        Create a new categorical percentage question.

        :param name: A pythonic name for the question.
        :param text: The text asked in the question.
        :param categories: The list of possible choices.
        :param data: Optional pandas Series of responses. Each non-null response
                     should be a Dict[str, float] mapping categories to
                     percentages.
        """
        self._set_name_and_text(name, text)
        self._set_categories(categories)
        self.data = data

    def _validate_data(self, data: Series):

        data = data.dropna()
        values = Series([
            value for answer in data.values
            for value in answer.values()
        ])
        if (values < 0).sum() != 0:
            raise ValueError(
                'Data for CategoricalPercentageQuestion must be non-negative.'
            )
        sums = data.map(lambda d: sum(list(d.values())))
        if (sums > 100).sum() != 0:
            raise ValueError(
                'Answers to CategoricalPercentageQuestion cannot sum to more '
                'than 100%'
            )

    def make_features(self, answers: Series = None, drop_na: bool = True,
                      naming: str = '{{name}}: {{choice}}') -> DataFrame:
        """
        Create DataFrame of features for use in ML.

        :param answers: Answers to the Question from a Survey. If left as None
                        then use the Question's attached data.
        :param drop_na: Whether to drop null rows (rows where respondent was not
                        asked a question).
        :param naming: Pattern to use to name the columns.
                       '{{name}}' will be substituted with the name of the
                       question.
                       '{{choice}}' will be substituted with the name of the
                       choice.
        """
        if answers is None:
            answers = self._data
        if drop_na:
            # drop respondents that weren't asked the question
            answers = answers.dropna()
        feature_list = []
        categories = self.category_names
        if len(answers) > 0:
            # create features
            for _, answer in answers.iteritems():
                if isnull(answer):
                    feature_list.append({})
                else:
                    feature_list.append(answer)
            features = DataFrame(feature_list)
            for category in categories:
                if category not in features.columns:
                    features[category] = 0
            some_values = isnull(features).sum(axis=1) < len(categories)
            features.loc[some_values] = features.loc[some_values].fillna(0)
            features = features[categories]
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

    def plot_distribution(
            self, data: Optional[Series] = None,
            drop_na: bool = True,
            transpose: bool = None,
            color: str = 'C0', pct_size: int = None,
            label_mappings: Optional[Dict[str, str]] = None,
            grid: bool = False,
            max_axis_label_chars: Optional[int] = None,
            title: Optional[str] = None,
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            ax: Optional[Axes] = None,
            **kwargs
    ):
        """
        Plot the distribution of answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param drop_na: Whether to drop null responses from the dataset
                        (affects % calculations).
        :param transpose: Whether to transpose the labels to the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        :param color: Color or list of colors for the bars.
        :param pct_size: Font size for the percent markers.
        :param label_mappings: Optional dict of replacements for labels.
        :param grid: Whether to show a plot grid or not.
        :param max_axis_label_chars: Maximum number of characters in axis labels
                                     before wrapping.
        :param title: Axes title.
        :param x_label: Label for the x-axis.
        :param y_label: Label for the y-axis.
        """
        if data is None:
            data = self._data
        if data is None:
            raise ValueError('No data!')
        if title is None:
            title = self.text
        if x_label is None:
            x_label = self.name if not transpose else '# Respondents'
        if y_label is None:
            y_label = '# Respondents' if not transpose else self.name
        # TODO: finish this
