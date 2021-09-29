from typing import Optional, Union, List

from pandas import Series, cut, qcut, concat, IntervalIndex

from survey.mixins.data_mixins import NumericDataMixin
from survey.mixins.data_types.continuous_1d_mixin import Continuous1dMixin
from survey.mixins.data_validation.positive_measure_validation_mixin import \
    PositiveMeasureValidationMixin
from survey.mixins.named import NamedMixin
from survey.questions.single_choice_question import SingleChoiceQuestion
from survey.questions._abstract.question import Question


class PositiveMeasureQuestion(
    NamedMixin,
    NumericDataMixin,
    PositiveMeasureValidationMixin,
    Continuous1dMixin,
    Question
):
    """
    A question where the answer can be zero or any positive real number.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new Positive Measure question.

        :param name: A pythonic name for the question.
        :param text: The text of the question.
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        if data is not None:
            try:
                data = data.astype(int)
            except ValueError:
                data = data.astype(float)
        self.data = data

    def to_single_choice(
            self,
            method: str,
            categories: Union[int, List[float], IntervalIndex]
    ) -> SingleChoiceQuestion:
        """
        Quantize the data and convert to a SingleChoiceQuestion.

        :param method: Pandas method to slice the data.
                       One of {'cut', 'qcut', 'bins'}.
        :param categories: Number of categories (for 'cut' and 'qcut'),
                           or list of bin edges or IntervalIndex (for 'cut').
        """
        if method == 'cut':
            data = cut(self.data, categories)
        elif method == 'qcut':
            data = qcut(x=self.data, q=categories, duplicates='drop')
        else:
            raise ValueError("method must be one of {'cut', 'qcut'}")
        return SingleChoiceQuestion(
            name=self.name, text=self.text,
            categories=data.cat.categories.to_list(),
            ordered=True, data=data
        )

    def stack(self, other: 'PositiveMeasureQuestion',
              name: Optional[str] = None,
              text: Optional[str] = None) -> 'PositiveMeasureQuestion':

        if self.data.index.names != other.data.index.names:
            raise ValueError('Indexes must have the same names.')
        new_data = concat([self.data, other.data])
        new_question = PositiveMeasureQuestion(
            name=name or self.name,
            text=text or self.text,
            data=new_data
        )
        new_question.survey = self.survey
        return new_question

    def __repr__(self):

        return (f"PositiveMeasureQuestion("
                f"\n\tname='{self.name}',"
                f"\n\ttext='{self.text}'"
                f"\n)")
